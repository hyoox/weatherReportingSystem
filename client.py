import asyncio
import json
import aiohttp

async def send_weather_request(city):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://localhost:8080/weather') as ws:
            await ws.send_str(city)
            response = await ws.receive()
            weather_data = json.loads(response.data)

            # Extract weather information from the JSON response
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']

            # Print the weather information in a more readable format
            print(f"Weather in {city}:")
            print(f"Temperature: {temperature} °C")
            print(f"Humidity: {humidity}%")
            print(f"Description: {description}")

async def start_client():
    while True:
        city = input("Enter a city name to get its weather (or 'quit' to exit): ")
        if city.lower() == 'quit':
            break
        await send_weather_request(city)

if __name__ == "__main__":
    asyncio.run(start_client())