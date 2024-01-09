import json

DB_FILE = "weather_data.json"

def save_weather_data(city, weather_data):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[city] = data.get(city, []) + [weather_data]

    with open(DB_FILE, "w") as file:
        json.dump(data, file)

def get_weather_data(city):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            return data.get(city, [])
    except FileNotFoundError:
        return []
