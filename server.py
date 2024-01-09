import asyncio
import json
import websockets
import ssl
from utils import fetch_weather
from database import save_weather_data, get_weather_data
from auth import authenticate, is_admin

# Create an SSL context for the server
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Load the server's certificate and private key
ssl_context.load_cert_chain('localhost.pem', 'localhost-key.pem')

# Initialize dictionaries to store the clients and their usernames
clients = {}
usernames = {}

# Define the function to handle client connections
async def handle_client(websocket, path):
    # Initialize the client with no username
    clients[websocket] = None
    print("New client on login screen!")

    try:
        # Process incoming messages
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
                username = clients[websocket]
                print(f"{username} requested weather for {city}")
                # Fetch the weather data
                weather_data = fetch_weather(city)
                if weather_data:
                    # If the weather data is found, save it and send it to the client
                    save_weather_data(city, weather_data)
                    await websocket.send(json.dumps(weather_data))
                else:
                    # If the weather data is not found, send an error message
                    await websocket.send(json.dumps({"error": "Data not found, please try again with another city name."}))

            # Handle history request messages
            elif data["type"] == "get_history":
                username = clients[websocket]
                # Check if the user is authenticated and is an admin
                # TODO: fix it here tommorow
                if not username or not is_admin(username):
                    # If not, send an error message
                    await websocket.send(json.dumps({"error": "Unauthorized"}))
                else:
                    city = data["city"]
                    # Fetch the weather history
                    history = get_weather_data(city)
                    # Send the weather history to the client
                    await websocket.send(json.dumps({"history": history}))

            # Handle heartbeat messages
            elif data["type"] == "heartbeat":
                username = clients[websocket]
                print(f"Heartbeat received from {username}")

    # Handle unexpected disconnections
    except websockets.exceptions.ConnectionClosed:
        username = clients.pop(websocket, "Unknown")
        print(f"{username} disconnected unexpectedly")
    finally:
        # Handle normal disconnections
        if websocket in clients:
            username = clients.pop(websocket, "Unknown")
            print(f"{username} disconnected")

# Define the main function
async def main():
    # Start the WebSocket server
    async with websockets.serve(handle_client, "localhost", 8765, ssl=ssl_context):
        print("Server started")
        # Keep the server running forever
        await asyncio.Future()

# Run the main function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())