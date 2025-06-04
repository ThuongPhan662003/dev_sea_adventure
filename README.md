# 🐙 Dev Sea Adventure

**Dev Sea Adventure** là một game chiến thuật theo lượt nhiều người chơi, nơi bạn điều khiển lập trình viên săn lùng source code dưới đáy biển. Game sử dụng **Pygame** cho phần client và **FastAPI + WebSocket** cho phần server, áp dụng thuật toán **Token Ring** để điều phối lượt chơi một cách công bằng và đồng bộ.

---

## 🚀 Tính năng nổi bật

- 🎮 Chơi nhiều người theo lượt với Token Ring
- 🌐 Kết nối client-server bằng WebSocket
- 🧠 Bản đồ dạng lưới có tile tương tác
- 💾 Lưu trữ dữ liệu người chơi và lịch sử bằng MySQL
- ⚙️ Mô hình tổ chức rõ ràng, dễ mở rộng (OOP + MVC)

---

## 🧩 Công nghệ sử dụng

| Thành phần        | Công nghệ                          |
| ----------------- | ---------------------------------- |
| Frontend (Client) | `Pygame`, `asyncio`                |
| Backend (Server)  | `FastAPI`, `WebSocket`, `SQLModel` |
| Cơ sở dữ liệu     | `MySQL`                            |
| Mạng              | `WebSocket`, Token Ring Protocol   |

---

## 🛠️ Cài đặt & chạy local

### 1. Clone dự án

```bash
git clone https://github.com/ThuongPhan662003/dev_sea_adventure.git
cd dev_sea_adventure
```

### 2. Thiết lập môi trường ảo ở ngoài 2 folder

```bash
python -m venv venv
source venv/bin/activate      # Unix/macOS
venv\Scripts\activate         # Windows
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Khởi chạy Server FastAPI

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 5001
```

> 🔧 Server sẽ chạy tại: `ws://localhost:5000/ws`

### 5. Khởi chạy Game Client (Pygame)

```bash
cd client
python main.py
```

> 💡 Mỗi client tương ứng với một người chơi (mở nhiều terminal để test multi-user)

---

## 🗂️ Cấu trúc thư mục

```
dev_sea_adventure/
├── client/                   # Pygame UI & Game loop
│   ├── main.py               # Client launcher
│   ├── network/              # WebSocket client
│   ├── scenes/               # UI scenes
│   └── components/           # Dice, Tile, Character...
├── server/                   # FastAPI backend
│   ├── main.py               # WebSocket handler
│   ├── models.py             # SQLModel ORM
│   ├── database.py           # DB connection
│   └── utils/                # Token ring logic
├── assets/                   # Ảnh, âm thanh, sprite
├── requirements.txt          # Thư viện Python
└── README.md
```

---

## 🔄 Luật chơi (Tóm tắt)

1. Người chơi đầu tiên giữ **Token**
2. Khi đến lượt, người chơi:
   - Tung xúc xắc để di chuyển
   - Tương tác với tile (thu thập source code, tránh đá…)
   - Gửi token cho người tiếp theo
3. Server điều phối lượt bằng thuật toán **Token Ring**

---

## 🧪 Mẹo test đa người chơi

- Mở nhiều terminal/chạy nhiều cửa sổ `main.py` (tên người chơi khác nhau)
- Player đầu tiên là **host**, có quyền `start game`
- Server xử lý token và gửi map/data cho client tương ứng

---

## 💡 Ghi chú kỹ thuật

- Đảm bảo `MySQL` đã chạy với các bảng được định nghĩa trước
- Server hiện hỗ trợ tối đa **4 người chơi đồng thời**
- Tính năng như **hành động (action), bản đồ nâng cao**, sẽ được mở rộng thêm

---

## 👨‍💻 Tác giả

- **ThuongPhan662003**  
  [GitHub Profile](https://github.com/ThuongPhan662003)

---

## 📜 Giấy phép

Dự án sử dụng [MIT License](LICENSE).
