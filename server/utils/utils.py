import socket


def get_local_ip():
    """Lấy địa chỉ IP nội bộ (IPv4) đang hoạt động."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Kết nối ảo ra ngoài để buộc hệ thống chọn interface phù hợp
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


client_ip = get_local_ip()
print(f"[CLIENT] My IP: {client_ip}")
