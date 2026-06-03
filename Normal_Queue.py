from collections import deque
from datetime import datetime
from typing import Optional

class Customer:

    def __init__(self, name: str, call_type: str = "Thông thường"):
        self.name: str = name
        self.call_type: str = call_type
        self.joined_at: datetime = datetime.now()
        self.position: int = 0          # Được NormalQueue cập nhật sau khi thêm vào

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
            "customer_type": "Thường",
        }


class NormalQueue:
 

    def __init__(self, max_size: int = 50):
        
        self._queue: deque[Customer] = deque()
        self.max_size: int = max_size
        self._served_count: int = 0     # Tổng số khách đã được phục vụ

    # ------------------------------------------------------------------
    # Thêm khách vào hàng đợi (Enqueue)
    # ------------------------------------------------------------------

    def enqueue(self, customer: Customer) -> bool:
        
        if not isinstance(customer, Customer):
            raise TypeError(f"Chỉ chấp nhận kiểu Customer, nhận được: {type(customer)}")

        # Kiểm tra giới hạn tối đa
        if self.max_size > 0 and len(self._queue) >= self.max_size:
            return False    # Hàng đợi đã đầy

        self._queue.append(customer)                # Thêm vào cuối — O(1)
        self._update_positions()                    # Cập nhật số thứ tự
        return True

    # ------------------------------------------------------------------
    # Lấy khách ra phục vụ (Dequeue)
    # ------------------------------------------------------------------

    def dequeue(self) -> Optional[Customer]:

        if self.is_empty():
            return None

        customer = self._queue.popleft()    # Lấy từ đầu — O(1)
        self._served_count += 1
        self._update_positions()            # Cập nhật lại số thứ tự
        return customer

    # ------------------------------------------------------------------
    # Xem khách đầu hàng (Peek) — không lấy ra
    # ------------------------------------------------------------------

    def peek(self) -> Optional[Customer]:
        
        if self.is_empty():
            return None
        return self._queue[0]

    # ------------------------------------------------------------------
    # Xoá một khách cụ thể khỏi hàng đợi
    # ------------------------------------------------------------------

    def remove(self, name: str) -> bool:
        
        for customer in self._queue:
            if customer.name == name:
                self._queue.remove(customer)
                self._update_positions()
                return True
        return False

    # ------------------------------------------------------------------
    # Truy vấn thông tin
    # ------------------------------------------------------------------

    def get_all(self) -> list[dict]:
        
        return [customer.to_dict() for customer in self._queue]

    def size(self) -> int:
        """Trả về số khách hiện đang chờ trong hàng đợi."""
        return len(self._queue)

    def is_empty(self) -> bool:
        """Trả về True nếu hàng đợi không có khách nào."""
        return len(self._queue) == 0

    def is_full(self) -> bool:
        """Trả về True nếu hàng đợi đã đạt giới hạn tối đa."""
        if self.max_size <= 0:
            return False
        return len(self._queue) >= self.max_size

    def get_served_count(self) -> int:
        """Trả về tổng số khách đã được phục vụ kể từ khi khởi động."""
        return self._served_count

    def get_wait_position(self, name: str) -> int:
        
        for i, customer in enumerate(self._queue):
            if customer.name == name:
                return i + 1
        return -1
 
    def clear(self) -> None:
        """Xoá toàn bộ hàng đợi (dùng khi reset hệ thống hoặc cuối ca)."""
        self._queue.clear()

    # ------------------------------------------------------------------
    # Phương thức nội bộ
    # ------------------------------------------------------------------

    def _update_positions(self) -> None:
        """Cập nhật lại thuộc tính `position` cho từng khách sau mỗi thay đổi."""
        for i, customer in enumerate(self._queue):
            customer.position = i + 1

    def __len__(self) -> int:
        return len(self._queue)

    def __repr__(self) -> str:
        return f"NormalQueue(size={self.size()}, max_size={self.max_size}, served={self._served_count})"


# ---------------------------------------------------------------------------
# Hàm tiện ích (Utility Functions) — dùng trực tiếp từ app.py / frontend
# ---------------------------------------------------------------------------

def create_queue(max_size: int = 50) -> NormalQueue:
    
    return NormalQueue(max_size=max_size)


def add_customer(queue: NormalQueue, name: str, call_type: str = "Thông thường") -> dict:
    
    if not name or not name.strip():
        return {"success": False, "message": "Tên khách hàng không được để trống."}

    customer = Customer(name=name.strip(), call_type=call_type)
    success = queue.enqueue(customer)

    if success:
        return {
            "success": True,
            "message": f" Đã thêm khách '{customer.name}' vào hàng đợi. Vị trí: #{customer.position}",
            "position": customer.position,
            "customer": customer.to_dict(),
        }
    else:
        return {
            "success": False,
            "message": f" Hàng đợi đã đầy ({queue.max_size} khách). Không thể thêm '{name}'.",
        }


def serve_next_customer(queue: NormalQueue) -> dict:
    
    customer = queue.dequeue()

    if customer:
        return {
            "success": True,
            "message": f"🎧 Đang phục vụ: {customer.name} | Loại: {customer.call_type}",
            "customer": customer.to_dict(),
        }
    else:
        return {
            "success": False,
            "message": "ℹ️ Hàng đợi đang trống. Không có khách nào cần phục vụ.",
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


# ---------------------------------------------------------------------------
# Demo / Kiểm thử nhanh khi chạy trực tiếp file này
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("   DEMO: Hàng đợi FIFO — Call Center System")
    print("=" * 55)

    q = create_queue(max_size=5)

    # Thêm khách vào hàng đợi
    for name, call_type in [
        ("Nguyễn Văn An",   "Hỗ trợ kỹ thuật"),
        ("Trần Thị Bình",   "Thanh toán hoá đơn"),
        ("Lê Minh Châu",    "Tư vấn sản phẩm"),
        ("Phạm Quốc Dũng",  "Khiếu nại dịch vụ"),
    ]:
        result = add_customer(q, name, call_type)
        print(result["message"])

    print(f"\n Hàng đợi hiện tại: {q.size()} khách đang chờ")
    print("-" * 55)
    for c in q.get_all():
        print(f"  #{c['position']}  {c['name']}  |  {c['call_type']}  |  {c['joined_at']}")

    print("\n Phục vụ lần lượt...")
    print("-" * 55)
    for _ in range(3):
        result = serve_next_customer(q)
        print(result["message"])

    print(f"\n Còn lại: {q.size()} khách | Đã phục vụ: {q.get_served_count()} khách")
    status = get_queue_status(q)
    print(f"   Khách tiếp theo: {status['next_customer']['name'] if status['next_customer'] else 'Không có'}")
    print("=" * 55)