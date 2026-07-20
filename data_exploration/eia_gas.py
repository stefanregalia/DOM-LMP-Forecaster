"""
Exploration of the EIA natural gas data, which will be used as a feature in the DOM LMP forecaster
"""

# Importing necessary libraries
import requests
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

# Getting the API key from environment variables
BASE = "https://api.eia.gov/v2"
KEY = os.environ["EIA_KEY"]

# Defining params for the EIA API request
params = {
    "api_key": KEY,
    "frequency": "daily", # Only updates once a day
    "data[0]": "value", # value is price 
    "facets[series][]": "RNGWHHD", # Series ID for Henry Hub Natural Gas Spot Price
    "sort[0][column]": "period", # Sort by period (date)
    "sort[0][direction]": "desc", # Sort dates in descending order
    "length": 5, # Get the last 5 days of data
}

# Fetching the necessary data from the EIA API
r = requests.get(f"{BASE}/natural-gas/pri/fut/data/", params=params, timeout=30)
r.raise_for_status()
gas_data = r.json()

# Printing the last 5 days of natural gas price data
for row in gas_data["response"]["data"]:
    print(row)