"""
Inspecting one week of weather data historical forecasts from Open Meteo API to add as 
predictive features to the model
"""

# Importing necessary libraries
import requests

# Getting the base URL for the Open Meteo API historical forecast endpoint
BASE = "https://historical-forecast-api.open-meteo.com/v1/forecast"

params = {
    "latitude": 39.04,  # Latitude for Ashburn, VA (Heavy data-center concentration)
    "longitude": -77.49,  # Longitude for Ashburn, VA (Heavy data-center concentration)
    "start_date": "2024-06-01",  # Start date for the forecast
    "end_date": "2024-06-07",  # End date for the forecast
    "hourly": "temperature_2m_previous_day1,wind_speed_10m_previous_day1,cloud_cover_previous_day1",  # Features
    "timezone": "America/New_York", 
}
# Fetching the necessary data
r = requests.get(BASE, params=params, timeout=30)
r.raise_for_status()
weather_data = r.json()

print("Weather Data Keys:", weather_data.keys())
print("Hourly Weather Data Keys:", weather_data["hourly"].keys())

for w in weather_data["hourly"]:
    print(w, weather_data["hourly"][w][:5])  # Printing the first 5 rows of each feature