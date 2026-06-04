from platform import node


class PriorityQueue:
    def __init__(self):
        self.head = None
 
    def is_empty(self):
        return self.head is None
 
    def enqueue_priority(self, call):
        score = call.effective_score()
 
        # Fast path: empty queue, or new call beats the current head
        if self.is_empty() or score > self.head.effective_score():
            call.next = self.head
            self.head = call
            return
 
        current = self.head
        while (current.next is not None
               and current.next.effective_score() >= score):
            current = current.next
 
        call.next    = current.next
        current.next = call
 
    def reorder(self):
        if self.is_empty() or self.head.next is None:
            return  # 0 or 1 node — already sorted
 
        sorted_head = None  # head of the growing sorted sub-list
 
        while self.head is not None:
            # Pick the node with the highest effective_score from unsorted
            prev_max  = None
            prev      = None
            curr      = self.head
            best_prev = None
            best      = self.head
 
            while curr is not None:
                if curr.effective_score() > best.effective_score():
                    best_prev = prev
                    best      = curr
                prev = curr
                curr = curr.next
 
            # Detach `best` from the unsorted list
            if best_prev is None:
                self.head = best.next
            else:
                best_prev.next = best.next
            best.next = None
 
            # TRƯỚC — mỗi lần append phải scan từ đầu
            if sorted_head is None:
                sorted_head = best
            else:
                node = sorted_head
                while node.next is not None:  # O(n) mỗi lần!
                    node = node.next
                node.next = best

            # SAU — trỏ thẳng vào tail, O(1)
            if sorted_head is None:
                sorted_head = best
            else:
                sorted_tail.next = best

            sorted_tail = best   # chung cho cả 2 trường hợp
 
        self.head = sorted_head
 
    def dequeue(self):
        """Remove and return the highest-priority call (head) — O(1)."""
        if self.is_empty():
            return None
        removed   = self.head
        self.head = self.head.next
        removed.next = None
        return removed
 
    def remove_call_by_id(self, call_id):
        """Remove any call by ID — O(n)."""
        if self.is_empty():
            return False
 
        if self.head.call_id == call_id:
            removed   = self.head
            self.head = self.head.next
            removed.next = None
            return True
 
        current = self.head
        while current.next is not None:
            if current.next.call_id == call_id:
                removed      = current.next
                current.next = removed.next
                removed.next = None
                return True
            current = current.next
        return False