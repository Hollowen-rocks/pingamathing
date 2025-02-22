import asyncio
import websockets
import json
import time

connected_clients = {}

async def handle_client(websocket, path):
    global connected_clients
    try:
        async for message in websocket:
            data = json.loads(message)
            user_id = data["userId"]

            if user_id not in connected_clients:
                connected_clients[user_id] = {
                    "name": data["name"],
                    "currentPing": data["currentPing"],
                    "avgPing": data["avgPing"],
                    "last_update": time.time()
                }
            
            client_data = connected_clients[user_id]
            client_data["currentPing"] = data["currentPing"]
            client_data["avgPing"] = sum(client_data["currentPing"] for _ in range(10)) // 10
            client_data["last_update"] = time.time()

            # Send updated client list to everyone
            for client in connected_clients:
                await websocket.send(json.dumps(connected_clients))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def start_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 5000)
    print("WebSocket server started on port 5000")
    await server.wait_closed()

asyncio.run(start_server())
