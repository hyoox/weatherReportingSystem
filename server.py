import asyncio
import json
import websockets
import ssl
from utils import fetch_weather

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('localhost.pem', 'localhost-key.pem')

client_counter = 0  # Counter to assign unique IDs to clients
clients = {}  # Dictionary to keep track of client IDs and websockets

async def handle_client(websocket, path):
    global client_counter
    client_id = client_counter
    clients[client_id] = websocket
    client_counter += 1
    print(f"Client#{client_id} connected")

    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "weather_request":
                city = data["city"]
                print(f"Client#{client_id} requested weather for {city}")
                weather_data = fetch_weather(city)
                if weather_data:
                    await websocket.send(json.dumps(weather_data))
                else:
                    await websocket.send(json.dumps({"error": "Data not found, please try again with another City name."}))
            elif data["type"] == "heartbeat":
                print(f"Heartbeat received from Client#{client_id}")
                # No response needed for heartbeat
    except websockets.exceptions.ConnectionClosed:
        pass  # This block may be left empty
    finally:
        print(f"Client#{client_id} disconnected")
        del clients[client_id]  # Remove client from the dictionary

async def main():
    async with websockets.serve(handle_client, "localhost", 8765, ssl=ssl_context):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
