"""
Backfilling script to get the historical energy generation data for different fuel types   
"""

# Importing necessary libraries
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import time
from pathlib import Path

# Defining the data directory path
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Loading environment variables
load_dotenv()

BASE = "https://api.pjm.com/api/v1"
HEADERS = {"Ocp-Apim-Subscription-Key": os.environ["PJM_KEY"]}

# Query function to get data from PJM API, added retries now for entire backfill
def query_pjm(data, retries = 3, **kwargs):
    """
    Function to query necessary data from the PJM API with retries in case of failure
    """
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{BASE}/{data}",
                headers=HEADERS,
                params={"rowCount": 25, "startRow": 1, **kwargs}, timeout = 30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                print(f"Request Failed ({e}), retrying in 30 seconds")
                time.sleep(30)
            else:
                raise

# Months to loop over
months = pd.date_range(start = '2024-01-01', end = '2026-07-01', freq = 'MS')

for month in months:
    start = month
    end = pd.offsets.MonthEnd(1) + month # Last day of the month

    date_range = f"{start.strftime('%m-%d-%Y')} 00:00 to {end.strftime('%m-%d-%Y')} 23:59" # PJM format

    # Resuming if parquet has already been created
    filepath = DATA_DIR / f"gen_by_fuel_{month.strftime('%Y_%m')}.parquet"

    if filepath.exists():
        continue

    # Querying PJM for generation by fuel type historical data for each hour of each month
    result = query_pjm('gen_by_fuel', datetime_beginning_ept = date_range, rowCount = 50000)

    fuel_gen_df = pd.DataFrame(result['items'])

    fuel_gen_df.to_parquet(filepath, engine = 'pyarrow') # Converting to parquet

    print(f"{month.strftime('%Y-%m')}: saved {len(fuel_gen_df)} rows")

    time.sleep(20) # Sleeping 20 seconds