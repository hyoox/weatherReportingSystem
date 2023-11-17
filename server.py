import asyncio
import json
import websockets
from utils import fetch_weather

# This is an asynchronous function that handles a weather request.
async def handle_weather_request(websocket, path):
    # This loop waits for a message from the client(s).
    async for message in websocket:
        # The message is expected to be a JSON string representing a city name.
        # json.loads parses the JSON string into a Python object.
        city = json.loads(message)
        # Fetch the weather data for the cit.
        weather_data = fetch_weather(city)
        # If weather data exists, send it back to the client(s).
        if weather_data:
            # json.dumps convert the Python object back into a JSON string.
            await websocket.send(json.dumps(weather_data))
        # If no weather data, send an error message back to the client(s).
        else:
            await websocket.send("Error fetching weather data.")

# Create a WebSocket server that listens on localhost port 8765
# The server uses the handle_weather_request function to handle requests
start_server = websockets.serve(handle_weather_request, "localhost", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
# Keep the server running forever
asyncio.get_event_loop().run_forever()