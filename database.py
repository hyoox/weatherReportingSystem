import json

# Define the name of the database file
DB_FILE = "weather_data.json"

# Define a function to save weather data for a city
def save_weather_data(city, weather_data):
    # Try to open the database file and load its contents
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
    # If the file doesn't exist, initialize an empty dictionary
    except FileNotFoundError:
        data = {}

    # Add the new weather data to the list of weather data for this city
    data[city] = data.get(city, []) + [weather_data]

    # Write the updated data back to the database file
    with open(DB_FILE, "w") as file:
        json.dump(data, file)

# Define a function to get the weather data for a city
def get_weather_data(city):
    # Try to open the database file and load its contents
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            # Return the list of weather data for this city, or an empty list if the city is not in the database
            return data.get(city, [])
    # If the file doesn't exist, return an empty list
    except FileNotFoundError:
        return []