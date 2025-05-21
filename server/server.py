import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import SERVER_HOST, SERVER_PORT
from token_ring import TokenRingServer

if __name__ == "__main__":
    server = TokenRingServer(host=SERVER_HOST, port=SERVER_PORT)
    server.start()
