import asyncio
import json
import websockets
import ssl
from utils import fetch_weather
from database import save_weather_data, get_weather_data
from auth import authenticate, is_admin, change_password

# Create an SSL context for secure connections
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Load the server's certificate and private key
ssl_context.load_cert_chain('localhost.pem', 'localhost-key.pem')

# A dictionary to keep track of connected clients and their usernames
clients = {}

# Coroutine to handle a client
async def handle_client(websocket, path):
    # Add the client to the clients dictionary with a username of None
    clients[websocket] = None
    print("New client on login screen!")

    try:
        # Loop over messages from the client
        async for message in websocket:
            # Parse the message as JSON
            data = json.loads(message)

            # Handle authentication messages
            if data["type"] == "authenticate":
                username = data["username"]
                password = data["password"]
                # Authenticate the user
                if authenticate(username, password):
                    # If authentication is successful, update the username for this client
                    clients[websocket] = username
                    await websocket.send(json.dumps({"status": "authenticated"}))
                    print(f"{username} authenticated successfully.")
                else:
                    # If authentication fails, send an error message
                    await websocket.send(json.dumps({"error": "Authentication failed"}))

            # Handle weather request messages
            elif data["type"] == "weather_request":
                city = data["city"]
                # Fetch the weather data for the city
                weather_data = fetch_weather(city)
                if weather_data:
                    # If the weather data is found, save it and send it to the client
                    save_weather_data(city, weather_data)
                    await websocket.send(json.dumps({"type": "weather_data", "data": weather_data}))
                    # Broadcast the weather data to all other clients
                    for client, username in clients.items():
                        if client != websocket:
                            await client.send(json.dumps({"type": "weather_broadcast", "data": weather_data, "city": city}))
                else:
                    # If the weather data is not found, send an error message
                    await websocket.send(json.dumps({"type": "error", "message": "Data not found"}))

            # Handle history request messages
            elif data["type"] == "get_history":
                username = clients[websocket]
                if username is None or not is_admin(username):
                    # Send an error message if the user is not authenticated or not an admin
                    await websocket.send(json.dumps({"error": "Unauthorized"}))
                else:
                    city = data["city"]
                    # Get the weather history for the city
                    weather_history = get_weather_data(city)
                    if weather_history:
                        # If the weather history is found, send it to the client
                        await websocket.send(json.dumps({"type": "history_data", "data": weather_history}))
                    else:
                        # If the weather history is not found, send an error message
                        await websocket.send(json.dumps({"type": "error", "message": "History data not found"}))

            # Handle heartbeat messages
            elif data["type"] == "heartbeat":
                username = clients[websocket]
                print(f"Heartbeat received from {username}")

            # Handle password change messages
            elif data["type"] == "change_password":
                username = clients[websocket]
                new_password = data["new_password"]
                if username:
                    # If the user is authenticated, change their password
                    change_password(username, new_password)
                    await websocket.send(json.dumps({"type": "password_changed"}))  
                else:
                    # If the user is not authenticated, send an error message
                    await websocket.send(json.dumps({"type": "error", "message": "User not authenticated"}))

    # Handle unexpected disconnections
    except websockets.exceptions.ConnectionClosed:
        username = clients.pop(websocket, "Unknown")
        print(f"{username} disconnected unexpectedly")
    finally:
        # Handle normal disconnections
        if websocket in clients:
            username = clients.pop(websocket, "Unknown")
            print(f"{username} disconnected")

# Coroutine to start the server
async def main():
    async with websockets.serve(handle_client, "localhost", 8765, ssl=ssl_context):
        print("Server started")
        # Wait forever
        await asyncio.Future()

# If this script is run directly, start the server
if __name__ == "__main__":
    asyncio.run(main())