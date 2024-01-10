import asyncio
import json
import websockets
import ssl
import threading

# Function to get user input
def get_user_input(prompt):
    return input(prompt)

# Create a default SSL context to establish a secure connection
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Global variable to check if the user is an admin
is_admin = False

# Create a queue for messages received from the server
message_queue = asyncio.Queue()

# Create a queue for broadcast messages
broadcast_queue = asyncio.Queue()

# Coroutine to receive messages from the server
async def receiver(websocket):
    while True:
        # Receive a message from the server
        message = await websocket.recv()
        # Parse the message as JSON
        data = json.loads(message)
        # If the message is a weather broadcast, put it in the broadcast queue
        if data["type"] == "weather_broadcast":
            await broadcast_queue.put(data)
        # Otherwise, put it in the message queue
        else:
            await message_queue.put(data)

# Coroutine to handle broadcast messages
async def handle_broadcasts():
    while True:
        # Wait for a broadcast message
        data = await broadcast_queue.get()
        # Extract the weather data from the message
        weather_data = data["data"]
        city = data["city"]
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        # Print the weather update
        print()
        print(f"Weather update for {city} broadcasted from other client:")
        print(f"Temperature: {temperature} °C")
        print(f"Humidity: {humidity}%")
        print(f"Description: {description}")
        # Print the prompt for the next command
        print("Enter 'weather' for weather info, 'history' for history, 'change' to change password, or 'quit' to exit: ")

# Coroutine to send a weather request to the server
async def send_weather_request(city, websocket):
    # Send a weather request to the server
    await websocket.send(json.dumps({"type": "weather_request", "city": city}))
    while True:
        # Wait for a response
        response = await message_queue.get()
        # If the response is weather data, print it
        if response.get("type") == "weather_data":
            weather_data = response["data"]
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            print(f"Weather in {city}:")
            print(f"Temperature: {temperature} °C")
            print(f"Humidity: {humidity}%")
            print(f"Description: {description}")
            break
        # If the response is an error, print the error message
        elif response.get("type") == "error":
            print(response["message"])
            break

# Coroutine to request weather history from the server
async def request_history(websocket):
    # Get the city name from the user
    city = input("Enter city name for history: ")
    # Send a history request to the server
    await websocket.send(json.dumps({"type": "get_history", "city": city}))
    try:
        while True:
            # Wait for a response
            response = await asyncio.wait_for(message_queue.get(), timeout=10.0)
            # If the response is history data, print it
            if response.get("type") == "history_data":
                history_data = response.get("data")
                break
    except asyncio.TimeoutError:
        # If no response is received within the timeout period, print a timeout message
        print("Response timed out.")
        return

    if history_data:
        print(f"Weather history for {city}:")
        for record in history_data:
            temp = record.get('main', {}).get('temp', 'N/A')
            humidity = record.get('main', {}).get('humidity', 'N/A')
            description = record.get('weather', [{}])[0].get('description', 'N/A')
            print(f"  - Temp: {temp}°C, Humidity: {humidity}%, Description: {description}")
    else:
        print("No history found for this city.")

# Coroutine to send a heartbeat message to the server every 10 seconds
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

# Coroutine to authenticate the user
async def authenticate(websocket):
    global is_admin
    # Get the username and password from the user
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    # Send an authenticate message to the server
    await websocket.send(json.dumps({"type": "authenticate", "username": username, "password": password}))
    # Wait for a response
    response = await websocket.recv()
    # Parse the response as JSON
    response_data = json.loads(response)
    # If the user is authenticated, set is_admin to True if the username is "admin"
    if response_data.get("status") == "authenticated":
        is_admin = username == "admin"
        return True
    # If the user is not authenticated, return False
    return False

# Coroutine to change the user's password
async def change_password(websocket):
    # Get the new password from the user
    new_password = get_user_input("Enter new password: ")
    # Send a change_password message to the server
    await websocket.send(json.dumps({"type": "change_password", "new_password": new_password}))
    try:
        while True:
            # Wait for a response
            response = await asyncio.wait_for(message_queue.get(), timeout=10.0)
            # If the response is a password_changed message, print a success message and break the loop
            if response.get("type") == "password_changed":
                print("Password changed successfully.")
                break
    except asyncio.TimeoutError:
        # If no response is received within the timeout period, print a timeout message
        print("Response timed out.")

# Coroutine to run the client loop
async def client_loop():
    # Connect to the server
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        # Authenticate the user
        if await authenticate(websocket):
            # If the user is authenticated, start the receiver, heartbeat, and broadcast tasks
            receiver_task = asyncio.create_task(receiver(websocket))
            heartbeat_task = asyncio.create_task(heartbeat(websocket))
            broadcast_task = asyncio.create_task(handle_broadcasts())
            while True:
                # Get the user's action
                action = await asyncio.get_event_loop().run_in_executor(None, get_user_input, "Enter 'weather' for weather info, 'history' for history, 'change' to change password, or 'quit' to exit: ")
                # If the user wants to quit, cancel the tasks and break the loop
                if action.lower() == 'quit':
                    receiver_task.cancel()
                    heartbeat_task.cancel()
                    broadcast_task.cancel()
                    break
                # If the user wants to see the weather history, check if they are an admin
                elif action.lower() == 'history':
                    if not is_admin:
                        print("Unauthorized: Only admins can access history.")
                    else:
                        await request_history(websocket)
                # If the user wants to see the weather, get the city name and send a weather request
                elif action.lower() == 'weather':
                    city = await asyncio.get_event_loop().run_in_executor(None, get_user_input, "Enter city name: ")
                    await send_weather_request(city, websocket)
                # If the user wants to change their password, call the change_password coroutine
                elif action.lower() == 'change':
                    await change_password(websocket)
        else:
            # If the user is not authenticated, print an error message
            print("Authentication failed.")

# If this script is run directly, start the client loop
if __name__ == "__main__":
    asyncio.run(client_loop())


