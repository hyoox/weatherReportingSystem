import asyncio
import json
import websockets
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def send_weather_request(city, websocket):
    await websocket.send(json.dumps({"type": "weather_request", "city": city}))
    response = await websocket.recv()
    weather_data = json.loads(response)

    if 'error' not in weather_data:
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        print(f"Weather in {city}:")
        print(f"Temperature: {temperature} °C")
        print(f"Humidity: {humidity}%")
        print(f"Description: {description}")
    else:
        print(weather_data['error'])

async def request_history(websocket):
    city = input("Enter city name for history: ")
    await websocket.send(json.dumps({"type": "get_history", "city": city}))
    response = await websocket.recv()
    history_data = json.loads(response).get("history", [])
    
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
            await asyncio.sleep(10)  # Send heartbeat every 10 seconds
        except websockets.exceptions.ConnectionClosed:
            break

async def authenticate(websocket):
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    await websocket.send(json.dumps({"type": "authenticate", "username": username, "password": password}))
    response = await websocket.recv()
    return json.loads(response).get("status") == "authenticated"

async def client_loop():
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        if await authenticate(websocket):
            asyncio.create_task(heartbeat(websocket))
            while True:
                action = input("Enter 'weather' for weather info, 'history' for history, or 'quit' to exit: ")
                if action.lower() == 'quit':
                    break
                elif action.lower() == 'history':
                    await request_history(websocket)
                elif action.lower() == 'weather':
                    city = input("Enter city name: ")
                    await send_weather_request(city, websocket)
        else:
            print("Authentication failed.")

if __name__ == "__main__":
    asyncio.run(client_loop())
