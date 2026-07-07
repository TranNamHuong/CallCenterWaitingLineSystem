import asyncio
import os
import uuid
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from db_setup import create_tables, seed_data, insert_call
from normal_queue_fifo import NormalQueue, Customer
from priority_queue_logic import PriorityQueue, Call

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Call Center Queue System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # "*" + credentials=True is invalid per the CORS spec; not needed here anyway
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup: fail loudly and specifically instead of a generic crash ---
try:
    create_tables()
    seed_data()
except Exception as e:
    # In production you'd log this to a file; for a class project, printing
    # a clear message beats a silent hang or an opaque traceback.
    print(f"[STARTUP ERROR] {e}")
    raise

fifo_queue = NormalQueue(max_size=50)
priority_queue = PriorityQueue()

# Single lock shared by both queues: enqueue/dequeue on either structure
# mutates shared state that /api/status also reads, so all three need
# to be serialized against each other, not just protected individually.
queue_lock = asyncio.Lock()

VIP_BASE_PRIORITY = 20
STANDARD_BASE_PRIORITY = 10  # unused directly (FIFO has no score), kept for reference


class CallRequest(BaseModel):
    name: str
    call_type: str
    customer_type: Literal["VIP", "Standard"] = "Standard"

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Customer name cannot be empty.")
        if len(v) > 100:
            raise ValueError("Customer name is too long (max 100 characters).")
        return v

    @field_validator("call_type")
    @classmethod
    def call_type_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Call type cannot be empty.")
        return v


@app.post("/api/enqueue")
async def enqueue_customer(req: CallRequest):
    async with queue_lock:
        try:
            if req.customer_type == "VIP":
                call = Call(
                    call_id=str(uuid.uuid4()),
                    name=req.name,
                    base_priority=VIP_BASE_PRIORITY,
                    call_type=req.call_type,
                )
                priority_queue.enqueue_priority(call)
                return {
                    "status": "success",
                    "message": f"Added VIP customer {req.name} to priority queue.",
                    "customer_type": "VIP",
                }
            else:
                new_customer = Customer(name=req.name, call_type=req.call_type)
                success = fifo_queue.enqueue(new_customer)
                if not success:
                    # 409 Conflict: valid request, but current server state can't accept it
                    raise HTTPException(status_code=409, detail="Standard queue is full. Try again shortly.")
                return {
                    "status": "success",
                    "message": f"Added {req.name} to FIFO queue.",
                    "position": new_customer.position,
                    "customer_type": "Standard",
                }
        except HTTPException:
            raise
        except Exception as e:
            # Anything unexpected (e.g. a bug in queue internals) -> 500, not a silent failure
            raise HTTPException(status_code=500, detail=f"Internal error while enqueueing: {e}")


@app.post("/api/serve")
async def serve_customer():
    """Serves the highest-priority VIP first (if any are waiting), else the
    next Standard customer. Changed from GET to POST: this endpoint mutates
    server state, which GET requests should never do."""
    async with queue_lock:
        try:
            served_from = None
            customer_dict = None

            if not priority_queue.is_empty():
                call = priority_queue.dequeue()
                served_from = "VIP"
                customer_dict = call.to_dict()
                db_ok = insert_call(
                    name=call.name,
                    customer_type="VIP",
                    call_type=call.call_type,
                    joined_at=call.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
            elif not fifo_queue.is_empty():
                customer = fifo_queue.dequeue()
                served_from = "Standard"
                customer_dict = customer.to_dict()
                db_ok = insert_call(
                    name=customer.name,
                    customer_type="Standard",
                    call_type=customer.call_type,
                    joined_at=customer.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                # 200, not an error: "queue empty" is a normal, expected state for a polling UI
                return {"status": "empty", "message": "Both queues are empty. No customer to serve."}

            response = {"status": "success", "customer": customer_dict, "served_from": served_from}
            if not db_ok:
                # Customer WAS served (removed from queue) even though logging failed.
                # Surface that distinction instead of hiding it.
                response["warning"] = "Customer served, but call log failed to save to database."
            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error while serving customer: {e}")


@app.get("/api/status")
async def queue_status():
    try:
        return {
            "vip_waiting": priority_queue.size(),
            "standard_waiting": fifo_queue.size(),
            "waiting_count": priority_queue.size() + fifo_queue.size(),
            "served_count": priority_queue.get_served_count() + fifo_queue.get_served_count(),
            "vip_customers": priority_queue.get_all(),
            "standard_customers": fifo_queue.get_all(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read queue status: {e}")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"index.html not found at {index_path}. Make sure it sits next to app.py.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)