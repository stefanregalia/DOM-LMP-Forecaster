"""
Loading all weather data for Ashburn, VA area since 2024 for prototyping
"""

# Importing necessary libraries
import requests
import pandas as pd

# Getting the base URL for the Open Meteo API historical forecast endpoint
BASE = "https://historical-forecast-api.open-meteo.com/v1/forecast"

params = {
    "latitude": 39.04,  # Latitude for Ashburn, VA (Heavy data-center concentration)
    "longitude": -77.49,  # Longitude for Ashburn, VA (Heavy data-center concentration)
    "start_date": "2024-01-01",  # Start date for the forecast
    "end_date": "2026-07-01",  # End date for the forecast
    "hourly": "temperature_2m_previous_day1,wind_speed_10m_previous_day1,cloud_cover_previous_day1",  # Features
    "timezone": "America/New_York", 
}
# Fetching the necessary data
r = requests.get(BASE, params=params, timeout=120)
r.raise_for_status()
weather_data = r.json()

# Converting the data to a pandas DataFrame then to parquet format for storage
weather_df = pd.DataFrame(weather_data["hourly"])
weather_df.to_parquet('../../data/weather_data.parquet', engine = 'pyarrow')

weather_length = len(weather_df)

print(f"{weather_length} rows of weather data have been loaded")
print(weather_df.head())
print(weather_df.iloc[20:30])   # Print a later sample of the data to verify that it is loading correctly
print(weather_df.isna().sum())  # total NaN count per column
