import asyncio
import json
import websockets
import ssl
from utils import fetch_weather
from database import save_weather_data, get_weather_data
from auth import authenticate, is_admin

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('localhost.pem', 'localhost-key.pem')

clients = {}
usernames = {}

async def handle_client(websocket, path):
    clients[websocket] = None  # Initialize with no username
    print("New client on login screen!")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "authenticate":
                username = data["username"]
                password = data["password"]
                if authenticate(username, password):
                    clients[websocket] = username  # Update username for this websocket
                    await websocket.send(json.dumps({"status": "authenticated"}))
                    print(f"{username} authenticated successfully.")
                else:
                    await websocket.send(json.dumps({"error": "Authentication failed"}))

            elif data["type"] == "weather_request":
                city = data["city"]
                username = clients[websocket]
                print(f"{username} requested weather for {city}")
                weather_data = fetch_weather(city)
                if weather_data:
                    save_weather_data(city, weather_data)
                    await websocket.send(json.dumps(weather_data))
                else:
                    await websocket.send(json.dumps({"error": "Data not found, please try again with another city name."}))

            elif data["type"] == "get_history":
                username = clients[websocket]
                if not username or not is_admin(username):
                    await websocket.send(json.dumps({"error": "Unauthorized"}))
                    continue
                city = data["city"]
                history = get_weather_data(city)
                await websocket.send(json.dumps({"history": history}))

            elif data["type"] == "heartbeat":
                username = clients[websocket]
                print(f"Heartbeat received from {username}")

    except websockets.exceptions.ConnectionClosed:
        username = clients.pop(websocket, "Unknown")
        print(f"{username} disconnected unexpectedly")
    finally:
        if websocket in clients:
            username = clients.pop(websocket, "Unknown")
            print(f"{username} disconnected")

async def main():
    async with websockets.serve(handle_client, "localhost", 8765, ssl=ssl_context):
        print("Server started")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
