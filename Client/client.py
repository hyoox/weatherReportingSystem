import asyncio
import json
import websockets
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

is_admin = False
message_queue = asyncio.Queue()

async def receiver(websocket):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        await message_queue.put(data)

async def send_weather_request(city, websocket):
    await websocket.send(json.dumps({"type": "weather_request", "city": city}))
    while True:
        response = await message_queue.get()
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
        elif response.get("type") == "error":
            print(response["message"])
            break

async def request_history(websocket):
    city = input("Enter city name for history: ")
    await websocket.send(json.dumps({"type": "get_history", "city": city}))
    try:
        while True:
            response = await asyncio.wait_for(message_queue.get(), timeout=10.0)
            if response.get("type") == "history_data":
                history_data = response.get("data")
                break
    except asyncio.TimeoutError:
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

async def heartbeat(websocket):
    while True:
        try:
            await websocket.send(json.dumps({"type": "heartbeat"}))
            await asyncio.sleep(10)
        except websockets.exceptions.ConnectionClosed:
            break

async def authenticate(websocket):
    global is_admin
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    await websocket.send(json.dumps({"type": "authenticate", "username": username, "password": password}))
    response = await websocket.recv()
    response_data = json.loads(response)
    if response_data.get("status") == "authenticated":
        is_admin = username == "admin"
        return True
    return False

async def client_loop():
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        if await authenticate(websocket):
            receiver_task = asyncio.create_task(receiver(websocket))
            heartbeat_task = asyncio.create_task(heartbeat(websocket))
            while True:
                action = input("Enter 'weather' for weather info, 'history' for history, or 'quit' to exit: ")
                if action.lower() == 'quit':
                    receiver_task.cancel()
                    heartbeat_task.cancel()
                    break
                elif action.lower() == 'history':
                    if not is_admin:
                        print("Unauthorized: Only admins can access history.")
                    else:
                        await request_history(websocket)
                elif action.lower() == 'weather':
                    city = input("Enter city name: ")
                    await send_weather_request(city, websocket)
        else:
            print("Authentication failed.")

if __name__ == "__main__":
    asyncio.run(client_loop())
