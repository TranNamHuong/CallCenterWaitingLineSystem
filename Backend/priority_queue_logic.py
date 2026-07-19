from __future__ import annotations

from datetime import datetime


class Call:
    def __init__(
        self,
        call_id: str,
        name: str,
        base_priority: int,
        call_type: str,
        joined_at: datetime | None = None,
    ):
        self.call_id = call_id
        self.name = name
        self.base_priority = base_priority
        self.call_type = call_type
        self.joined_at = joined_at or datetime.now()
        self.next = None

    def effective_score(self) -> float:
        waiting_time = (datetime.now() - self.joined_at).total_seconds()
        return self.base_priority + (waiting_time * 0.1)


class PriorityQueue:
    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def enqueue_priority(self, call):
        score = call.effective_score()

        if self.is_empty() or score > self.head.effective_score():
            call.next = self.head
            self.head = call
            return

        current = self.head
        while current.next is not None and current.next.effective_score() >= score:
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
            current = self.head
            best_prev = None
            best = self.head

            while current is not None:
                if current.effective_score() > best.effective_score():
                    best_prev = prev
                    best = current
                prev = current
                current = current.next

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
