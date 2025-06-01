import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_URI = os.getenv("MYSQL_URI", "")
    SOCKETIO_CORS_ALLOWED_ORIGINS = ["*"]
