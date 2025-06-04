import asyncio
import websockets
import json


async def test_ws():
    uri = "ws://localhost:5001/ws"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "join", "name": "Tester"}))
        print("✅ Đã gửi join.")
        while True:
            data = await ws.recv()
            print("📨 Nhận từ server:", data)


asyncio.run(test_ws())
