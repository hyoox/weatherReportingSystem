import asyncio
import json
import websockets

# This is an asynchronous function that sends a weather request for a given city.
async def send_weather_request(city):
    # Connect to the WebSocket server at ws://localhost:8765
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Send the city name to the server.
        # json.dumps converts the Python string into a JSON string.
        await websocket.send(json.dumps(city))
        # Wait for a response from the server.
        response = await websocket.recv()
        # Parse the JSON response into a Python object.
        weather_data = json.loads(response)

        # Extract weather information from the JSON response.
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        # Print the weather information in a more readable format.
        print(f"Weather in {city}:")
        print(f"Temperature: {temperature} °C")
        print(f"Humidity: {humidity}%")
        print(f"Description: {description}")

# This is an asynchronous function that starts the client(s).
async def start_client():
    # This loop asks the user for a city name and sends a weather request for that city.
    while True:
        city = input("Enter the name of City to get its weather (or type 'quit' to exit the application): ")
        if city.lower() == 'quit':
            break
        await send_weather_request(city)

# If this script is run directly (not imported as a module), start the client
if __name__ == "__main__":
    asyncio.run(start_client())