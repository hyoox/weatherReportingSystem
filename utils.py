import json
import requests

# API key for the OpenWeatherMap API
API_KEY = '2af3148bfd752e60a47e64137e475823'

# Function to fetch weather data for a given city
def fetch_weather(city):
    # The base URL of the OpenWeatherMap API
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # The parameters for the API request:
    # 'q' is the name of the city
    # 'appid' is your API key
    # 'units' is the unit for the temperature ('metric' means Celsius)
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric', 
    }

    # Send a GET request to the API
    response = requests.get(base_url, params=params)
    
    # If the request was successful (status code 200), parse the weather data from the response.
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    # If the request was not successful, return None.
    else:
        return None