from __future__ import annotations

from datetime import datetime
from typing import Any

from Backend.Normal_Queue import Customer, NormalQueue
from Backend.priority_queue_logic import Call, PriorityQueue
from Database.db_setup import add_active_call, complete_active_call, get_active_calls


class CallCenterQueueManager:
    """Coordinate normal and VIP queues while enforcing fairness between them."""

    def __init__(
        self,
        max_size: int = 50,
        max_consecutive_vip: int = 2,
        normal_wait_threshold_seconds: int = 120,
    ) -> None:
        self.normal_queue = NormalQueue(max_size=max_size)
        self.priority_queue = PriorityQueue()
        self.current_serving: dict[str, Any] | None = None
        self.vip_call_counter = 0
        self.consecutive_vip_served = 0
        self.max_consecutive_vip = max_consecutive_vip
        self.normal_wait_threshold_seconds = normal_wait_threshold_seconds
        self._restore_active_calls()

    def add_normal_customer(self, name: str, call_type: str) -> dict[str, Any]:
        if not name or not name.strip():
            return {"success": False, "message": "Customer name cannot be empty."}
        if self.get_total_waiting() >= self.normal_queue.max_size:
            return {
                "success": False,
                "message": f"Queue is full ({self.normal_queue.max_size} callers). Cannot add '{name}'.",
            }

        joined_at = datetime.now()
        queue_id = add_active_call(
            name=name.strip(),
            customer_type="Standard",
            call_type=call_type,
            joined_at=joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        customer = Customer(name=name.strip(), call_type=call_type, joined_at=joined_at, queue_id=queue_id)
        self.normal_queue.enqueue(customer)

        return {
            "success": True,
            "message": f"Added '{customer.name}' to the standard queue. Position: #{customer.position}",
            "position": customer.position,
            "customer": customer.to_dict(),
        }

    def add_vip_customer(self, name: str, service_type: str, vip_level: int) -> dict[str, Any]:
        if not name or not name.strip():
            return {"success": False, "message": "VIP customer name cannot be empty."}
        if self.get_total_waiting() >= self.normal_queue.max_size:
            return {
                "success": False,
                "message": f"Queue is full ({self.normal_queue.max_size} callers). Cannot add '{name}'.",
            }

        joined_at = datetime.now()
        level_mapping = {30: "Platinum VIP", 20: "Gold VIP", 10: "Silver VIP"}
        vip_rank = level_mapping.get(vip_level, "VIP")
        call_type = f"{vip_rank} - {service_type}"
        queue_id = add_active_call(
            name=name.strip(),
            customer_type="VIP",
            call_type=call_type,
            joined_at=joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            vip_level=vip_level,
        )
        new_call = Call(
            call_id=str(queue_id),
            name=name.strip(),
            base_priority=vip_level,
            call_type=call_type,
            joined_at=joined_at,
        )
        self.priority_queue.enqueue_priority(new_call)
        self.vip_call_counter = max(self.vip_call_counter, queue_id)

        return {
            "success": True,
            "message": f"Added VIP caller '{new_call.name}' to the priority queue.",
            "customer": {
                "id": new_call.call_id,
                "name": new_call.name,
                "call_type": new_call.call_type,
                "joined_at": new_call.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        }

    def serve_next_call(self) -> dict[str, Any]:
        self.priority_queue.reorder()

        if self._should_serve_normal_next():
            served_customer = self.normal_queue.dequeue()
            if served_customer is None:
                return self._empty_result()

            complete_active_call(
                call_id=served_customer.queue_id,
                name=served_customer.name,
                customer_type="Standard",
                call_type=served_customer.call_type,
                joined_at=served_customer.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.consecutive_vip_served = 0
            result = {
                "success": True,
                "customer_type": "Standard",
                "joined_at": served_customer.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
                "current_serving": {
                    "name": served_customer.name,
                    "type": "Standard",
                    "detail": served_customer.call_type,
                    "time": datetime.now().strftime("%H:%M:%S"),
                },
            }
            self.current_serving = result["current_serving"]
            return result

        if not self.priority_queue.is_empty():
            served_call = self.priority_queue.dequeue()
            if served_call is None:
                return self._empty_result()

            complete_active_call(
                call_id=int(served_call.call_id),
                name=served_call.name,
                customer_type="VIP",
                call_type=served_call.call_type,
                joined_at=served_call.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.consecutive_vip_served += 1
            result = {
                "success": True,
                "customer_type": "VIP",
                "joined_at": served_call.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
                "current_serving": {
                    "name": served_call.name,
                    "type": "VIP",
                    "detail": served_call.call_type,
                    "time": datetime.now().strftime("%H:%M:%S"),
                },
            }
            self.current_serving = result["current_serving"]
            return result

        return self._empty_result()

    def get_vip_queue_size(self) -> int:
        count = 0
        current = self.priority_queue.head
        while current is not None:
            count += 1
            current = current.next
        return count

    def get_total_waiting(self) -> int:
        return self.normal_queue.size() + self.get_vip_queue_size()

    def get_normal_queue_snapshot(self) -> list[dict[str, Any]]:
        return self.normal_queue.get_all()

    def get_vip_queue_snapshot(self) -> list[dict[str, Any]]:
        vip_table_data: list[dict[str, Any]] = []
        current = self.priority_queue.head
        position = 1
        while current is not None:
            vip_table_data.append(
                {
                    "Position": f"#{position}",
                    "Customer": current.name,
                    "Service": current.call_type,
                    "Joined": current.joined_at.strftime("%H:%M:%S"),
                    "Priority Score": f"{current.effective_score():.2f}",
                }
            )
            current = current.next
            position += 1
        return vip_table_data

    def fairness_summary(self) -> str:
        return (
            f"Fairness policy: allow up to {self.max_consecutive_vip} consecutive VIP calls, "
            f"or prioritize the standard queue when its first caller waits longer than "
            f"{self.normal_wait_threshold_seconds} seconds."
        )

    def _restore_active_calls(self) -> None:
        active_calls = get_active_calls()
        highest_id = 0

        for record in active_calls:
            highest_id = max(highest_id, int(record["id"]))
            joined_at = datetime.strptime(record["joined_at"], "%Y-%m-%d %H:%M:%S")
            if record["customer_type"] == "VIP":
                vip_call = Call(
                    call_id=str(record["id"]),
                    name=record["name"],
                    base_priority=int(record["vip_level"]),
                    call_type=record["call_type"],
                    joined_at=joined_at,
                )
                self.priority_queue.enqueue_priority(vip_call)
            else:
                customer = Customer(
                    name=record["name"],
                    call_type=record["call_type"],
                    joined_at=joined_at,
                    queue_id=int(record["id"]),
                )
                self.normal_queue.enqueue(customer)

        self.vip_call_counter = highest_id

    def _normal_waiting_seconds(self) -> float:
        next_normal = self.normal_queue.peek()
        if next_normal is None:
            return 0.0
        return max(0.0, (datetime.now() - next_normal.joined_at).total_seconds())

    def _should_serve_normal_next(self) -> bool:
        if self.normal_queue.is_empty():
            return False
        if self.priority_queue.is_empty():
            return True
        if self._normal_waiting_seconds() >= self.normal_wait_threshold_seconds:
            return True
        return self.consecutive_vip_served >= self.max_consecutive_vip

    def _empty_result(self) -> dict[str, Any]:
        self.current_serving = None
        return {
            "success": False,
            "message": "No callers are currently waiting in the queue.",
            "current_serving": None,
        }
