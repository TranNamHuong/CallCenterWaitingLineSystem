from datetime import datetime


class Call:
    def __init__(self, call_id: str, name: str, base_priority: int, call_type: str,
                 joined_at: datetime = None):
        self.call_id = call_id
        self.name = name
        self.base_priority = base_priority
        self.call_type = call_type
        self.joined_at = joined_at or datetime.now()
        self.next = None

    def effective_score(self) -> float:
        waiting_time = (datetime.now() - self.joined_at).total_seconds()
        return self.base_priority + (waiting_time * 0.1)

    # Added: needed so app.py can serialize this to JSON like Customer.to_dict()
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "call_type": self.call_type,
            "joined_at": self.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_type": "VIP",
            "call_id": self.call_id,
            "base_priority": self.base_priority,
            "effective_score": round(self.effective_score(), 2),
        }


class PriorityQueue:
    def __init__(self):
        self.head = None
        self._served_count = 0  # Added: app.py needs this for parity with NormalQueue

    def is_empty(self):
        return self.head is None

    def enqueue_priority(self, call):
        score = call.effective_score()
        if self.is_empty() or score > self.head.effective_score():
            call.next = self.head
            self.head = call
            return
        current = self.head
        while (current.next is not None
               and current.next.effective_score() >= score):
            current = current.next
        call.next = current.next
        current.next = call

    def reorder(self):
        if self.is_empty() or self.head.next is None:
            return
        sorted_head = None
        sorted_tail = None
        while self.head is not None:
            prev = None
            curr = self.head
            best_prev = None
            best = self.head
            while curr is not None:
                if curr.effective_score() > best.effective_score():
                    best_prev = prev
                    best = curr
                prev = curr
                curr = curr.next
            if best_prev is None:
                self.head = best.next
            else:
                best_prev.next = best.next
            best.next = None
            if sorted_head is None:
                sorted_head = best
                sorted_tail = best
            else:
                sorted_tail.next = best
                sorted_tail = best
        self.head = sorted_head

    def dequeue(self):
        if self.is_empty():
            return None
        removed = self.head
        self.head = self.head.next
        removed.next = None
        self._served_count += 1  # Added: was never incremented before
        return removed

    def remove_call_by_id(self, call_id):
        if self.is_empty():
            return False
        if self.head.call_id == call_id:
            removed = self.head
            self.head = self.head.next
            removed.next = None
            return True
        current = self.head
        while current.next is not None:
            if current.next.call_id == call_id:
                removed = current.next
                current.next = removed.next
                removed.next = None
                return True
            current = current.next
        return False

    # --- Added: app.py needs these to expose status via /api/status ---
    def size(self) -> int:
        count = 0
        current = self.head
        while current is not None:
            count += 1
            current = current.next
        return count

    def get_served_count(self) -> int:
        return self._served_count

    def get_all(self) -> list[dict]:
        self.reorder()  # ensure aging-adjusted order is current before display
        result = []
        current = self.head
        while current is not None:
            result.append(current.to_dict())
            current = current.next
        return result
