# Weather App

A desktop weather app built with Python and tkinter. Enter a city (or detect your location) to see the current weather, an hourly forecast and a 5-day forecast, with weather icons.

## Features

- Current weather: temperature, humidity, wind speed and a description
- Weather icon for the current condition
- Hourly forecast panel: the next 6 time slots
- 5-day forecast panel with highs and lows
- Celsius / Fahrenheit toggle that switches instantly
- Automatic location detection from your IP address (ipinfo.io)
- Errors shown inside the window: empty input, city not found, timeout, no internet, invalid API key

## Tech Stack

- Python 3.12
- requests (API calls)
- tkinter (GUI)
- Pillow (weather icons)
- OpenWeatherMap API (free tier) and ipinfo.io

## Setup

1. Get a free API key at openweathermap.org. A new key can take a while to activate.
2. Create a virtual environment: `py -3.12 -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install the libraries: `pip install -r requirements.txt`
5. Copy `config.example.py` to a new file named `config.py` and put your API key in it.
6. Start the app: `python weather.py`

`config.py` is listed in `.gitignore`, so your key is never uploaded.

## Notes

- The free OpenWeatherMap forecast gives data in 3-hour steps, so the "hourly" panel shows the next 6 steps (about 18 hours).
- Location detection by IP is approximate. It can show a nearby city, or the city of a VPN.

## Privacy

Your searches go to OpenWeatherMap. The location button also sends a request to ipinfo.io, which can see your IP address. Nothing is stored by this app.
