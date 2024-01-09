import asyncio
import json
import websockets
import ssl

# Create an SSL context for the client
ssl_context = ssl.create_default_context()
# Disable hostname checking and certificate verification for simplicity
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Define a function to send a weather request
async def send_weather_request(city, websocket):
    # Send the request
    await websocket.send(json.dumps({"type": "weather_request", "city": city}))
    # Wait for the response
    response = await websocket.recv()
    # Parse the response as JSON
    weather_data = json.loads(response)

    # If there is no error in the response, print the weather data
    if 'error' not in weather_data:
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        print(f"Weather in {city}:")
        print(f"Temperature: {temperature} °C")
        print(f"Humidity: {humidity}%")
        print(f"Description: {description}")
    else:
        # If there is an error in the response, print the error message
        print(weather_data['error'])

# Define a function to request the weather history for a city
async def request_history(websocket):
    city = input("Enter city name for history: ")
    # Send the request
    await websocket.send(json.dumps({"type": "get_history", "city": city}))
    # Wait for the response
    response = await websocket.recv()
    # Parse the response as JSON and get the history data
    history_data = json.loads(response).get("history", [])
    
    # If there is history data, print it
    if history_data:
        print(f"Weather history for {city}:")
        for record in history_data:
            temp = record.get('main', {}).get('temp', 'N/A')
            humidity = record.get('main', {}).get('humidity', 'N/A')
            description = record.get('weather', [{}])[0].get('description', 'N/A')
            print(f"  - Temp: {temp}°C, Humidity: {humidity}%, Description: {description}")
    else:
        # If there is no history data, print a message
        print("No history found for this city.")

# Define a function to send heartbeat messages
async def heartbeat(websocket):
    while True:
        try:
            # Send a heartbeat message
            await websocket.send(json.dumps({"type": "heartbeat"}))
            # Wait for 10 seconds
            await asyncio.sleep(10)
        except websockets.exceptions.ConnectionClosed:
            # If the connection is closed, break the loop
            break

# Define a function to authenticate the user
async def authenticate(websocket):
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    # Send the authentication request
    await websocket.send(json.dumps({"type": "authenticate", "username": username, "password": password}))
    # Wait for the response
    response = await websocket.recv()
    # Return True if the user is authenticated, False otherwise
    return json.loads(response).get("status") == "authenticated"

# Define the main client loop
async def client_loop():
    # Connect to the server
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        # Authenticate the user
        if await authenticate(websocket):
            # Start the heartbeat task
            asyncio.create_task(heartbeat(websocket))
            while True:
                # Ask the user for an action
                action = input("Enter 'weather' for weather info, 'history' for history, or 'quit' to exit: ")
                if action.lower() == 'quit':
                    # If the user wants to quit, break the loop
                    break
                elif action.lower() == 'history':
                    # If the user wants the history, request it
                    await request_history(websocket)
                elif action.lower() == 'weather':
                    # If the user wants the weather, request it
                    city = input("Enter city name: ")
                    await send_weather_request(city, websocket)
        else:
            # If authentication fails, print a message
            print("Authentication failed.")

# Run the main client loop
if __name__ == "__main__":
    asyncio.run(client_loop())