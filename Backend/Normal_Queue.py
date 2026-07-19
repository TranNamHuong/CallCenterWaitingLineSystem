from collections import deque
from datetime import datetime
from typing import Optional


class Customer:
    def __init__(
        self,
        name: str,
        call_type: str = "General",
        joined_at: datetime | None = None,
        queue_id: int | None = None,
    ):
        self.name: str = name
        self.call_type: str = call_type
        self.joined_at: datetime = joined_at or datetime.now()
        self.queue_id: int | None = queue_id
        self.position: int = 0

    def __repr__(self) -> str:
        return (
            f"Customer(name='{self.name}', "
            f"call_type='{self.call_type}', "
            f"joined_at='{self.joined_at.strftime('%H:%M:%S')}')"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "call_type": self.call_type,
            "joined_at": self.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            "position": self.position,
            "customer_type": "Standard",
        }


class NormalQueue:
    def __init__(self, max_size: int = 50):
        self._queue: deque[Customer] = deque()
        self.max_size: int = max_size
        self._served_count: int = 0

    def enqueue(self, customer: Customer) -> bool:
        if not isinstance(customer, Customer):
            raise TypeError(f"Expected Customer, received: {type(customer)}")
        if self.max_size > 0 and len(self._queue) >= self.max_size:
            return False

        self._queue.append(customer)
        self._update_positions()
        return True

    def dequeue(self) -> Optional[Customer]:
        if self.is_empty():
            return None

        customer = self._queue.popleft()
        self._served_count += 1
        self._update_positions()
        return customer

    def peek(self) -> Optional[Customer]:
        if self.is_empty():
            return None
        return self._queue[0]

    def remove(self, name: str) -> bool:
        for customer in self._queue:
            if customer.name == name:
                self._queue.remove(customer)
                self._update_positions()
                return True
        return False

    def get_all(self) -> list[dict]:
        return [customer.to_dict() for customer in self._queue]

    def size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def is_full(self) -> bool:
        if self.max_size <= 0:
            return False
        return len(self._queue) >= self.max_size

    def get_served_count(self) -> int:
        return self._served_count

    def get_wait_position(self, name: str) -> int:
        for i, customer in enumerate(self._queue):
            if customer.name == name:
                return i + 1
        return -1

    def clear(self) -> None:
        self._queue.clear()

    def _update_positions(self) -> None:
        for i, customer in enumerate(self._queue):
            customer.position = i + 1

    def __len__(self) -> int:
        return len(self._queue)

    def __repr__(self) -> str:
        return f"NormalQueue(size={self.size()}, max_size={self.max_size}, served={self._served_count})"


def create_queue(max_size: int = 50) -> NormalQueue:
    return NormalQueue(max_size=max_size)


def add_customer(queue: NormalQueue, name: str, call_type: str = "General") -> dict:
    if not name or not name.strip():
        return {"success": False, "message": "Customer name cannot be empty."}

    customer = Customer(name=name.strip(), call_type=call_type)
    success = queue.enqueue(customer)

    if success:
        return {
            "success": True,
            "message": f"Added '{customer.name}' to the queue. Position: #{customer.position}",
            "position": customer.position,
            "customer": customer.to_dict(),
        }
    return {
        "success": False,
        "message": f"Queue is full ({queue.max_size} callers). Cannot add '{name}'.",
    }


def serve_next_customer(queue: NormalQueue) -> dict:
    customer = queue.dequeue()
    if customer:
        return {
            "success": True,
            "message": f"Now serving: {customer.name} | Service: {customer.call_type}",
            "customer": customer.to_dict(),
        }
    return {
        "success": False,
        "message": "The queue is empty. No customer is waiting.",
    }


def get_queue_status(queue: NormalQueue) -> dict:
    next_customer = queue.peek()
    return {
        "waiting_count": queue.size(),
        "is_empty": queue.is_empty(),
        "is_full": queue.is_full(),
        "next_customer": next_customer.to_dict() if next_customer else None,
        "served_count": queue.get_served_count(),
        "all_customers": queue.get_all(),
    }
