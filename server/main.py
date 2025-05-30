# server/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from database import create_db_and_tables
from token_ring_server import router as token_ring_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tạo bảng nếu chưa có
create_db_and_tables()

# Đăng ký WebSocket router
app.include_router(token_ring_router)

# Chạy bằng lệnh:
# uvicorn server.main:app --host 0.0.0.0 --port 5000
