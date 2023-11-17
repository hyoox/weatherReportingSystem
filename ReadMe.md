# Weather Reporting System

Weather Reporting System is a simple Python application that utilizes WebSockets to retrieve weather data for a specified city from the OpenWeatherMap API.

## Prerequisites

Before proceeding, ensure you have met the following requirements:

1. Python 3.6 or later is installed.

2. Both the `websockets` and `requests` Python libraries are installed. You can install them using pip:

   ```bash
   pip install websockets requests
   ```

## Using Weather Reporting System

To use Weather Reporting System, follow these steps:

1. Clone this repository onto your local machine.

2. Navigate to the directory containing the code.

3. Run the server script:

   ```bash
   python server.py
   ```

4. In a separate terminal window, execute the client script:

   ```bash
   python client.py
   ```

The client script will prompt you to enter a city name. Type the name of a city and press Enter to retrieve its weather. To exit the application, type 'quit'.
