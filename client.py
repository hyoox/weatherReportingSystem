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

async def heartbeat(websocket):
    while True:
        try:
            await websocket.send(json.dumps({"type": "heartbeat"}))
            await asyncio.sleep(10)  # Send heartbeat every 10 seconds
        except websockets.exceptions.ConnectionClosed:
            break

async def client_loop():
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        asyncio.create_task(heartbeat(websocket))
        while True:
            city = input("Enter city name (or 'quit' to exit): ")
            if city.lower() == 'quit':
                break
            await send_weather_request(city, websocket)

if __name__ == "__main__":
    asyncio.run(client_loop())
