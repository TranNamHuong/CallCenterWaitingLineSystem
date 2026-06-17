from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import your custom logic
from db_setup import create_tables, seed_data, insert_call
from normal_queue_fifo import NormalQueue, Customer # Assume file is renamed to normal_queue_fifo.py

app = FastAPI(title="Call Center Queue System")

# Allow Frontend to communicate with Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize System
create_tables()
seed_data()
fifo_queue = NormalQueue(max_size=50)

# Request Model
class CallRequest(BaseModel):
    name: str
    call_type: str

@app.post("/api/enqueue")
async def enqueue_customer(req: CallRequest):
    new_customer = Customer(name=req.name, call_type=req.call_type)
    success = fifo_queue.enqueue(new_customer)
    if success:
        return {"status": "success", "message": f"Added {req.name} to queue.", "position": new_customer.position}
    return {"status": "error", "message": "Queue is full!"}

@app.get("/api/serve")
async def serve_customer():
    customer = fifo_queue.dequeue()
    if customer:
        # Save to database upon serving
        insert_call(
            name=customer.name, 
            customer_type="Standard", 
            call_type=customer.call_type, 
            joined_at=customer.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        return {"status": "success", "customer": customer.to_dict()}
    return {"status": "error", "message": "Queue is empty."}

@app.get("/api/status")
async def queue_status():
    return {
        "waiting_count": fifo_queue.size(),
        "served_count": fifo_queue.get_served_count(),
        "customers": fifo_queue.get_all()
    }

# Serve the HTML UI
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)