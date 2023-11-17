import asyncio
import json
import aiohttp
from aiohttp import web
from utils import fetch_weather

async def handle_weather_request(websocket, city):
    weather_data = fetch_weather(city)
    if weather_data:
        await websocket.send_json(weather_data)
    else:
        await websocket.send_str("Error fetching weather data.")

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await handle_weather_request(ws, msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    print('websocket connection closed')

    return ws

async def start_server():
    app = web.Application()
    app.router.add_route('GET', '/weather', handle_websocket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

if __name__ == "__main__":
    asyncio.run(start_server())