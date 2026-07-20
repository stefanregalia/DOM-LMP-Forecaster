"""
Exploration of the energy generation by fuel type data from PJM 
"""


# Importing necessary libraries
import os
import requests
from dotenv import load_dotenv

# Loading environment variables

load_dotenv()

# Getting the API key from environment variables 
BASE = "https://api.pjm.com/api/v1"
HEADERS = {"Ocp-Apim-Subscription-Key": os.environ["PJM_KEY"]}


# Query function to get data from PJM API
def query_pjm(data, **kwargs):
    """
    Function to query the PJM API for any data and the parameters listed. Queries
    only 25 rows from the API for exploration unless that value is overriden in the kwargs.
    """
    r = requests.get(
        f"{BASE}/{data}", 
        headers=HEADERS, 
        params={"rowCount": 25, "startRow": 1, **kwargs}, timeout = 30)
    r.raise_for_status()
    return r.json()


# Printing 10 rows of energy generation by fuel type 

result = query_pjm('gen_by_fuel', datetime_beginning_ept="LastWeek", rowCount=10)

for row in result["items"]:
    print(row)
