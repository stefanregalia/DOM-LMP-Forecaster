""" Finding the identifier for DOM in rt_hrl_lmps so that 
we can explore the actual data from PJM for the DOM zone"""

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


# Pulling zonal aggregate rows (1 per zone) to find the identifier for DOM in rt_hrl_lmps

result = query_pjm('rt_hrl_lmps', type='ZONE', datetime_beginning_ept="LastWeek")

print("Total Rows:", result['totalRows'])
for row in result["items"]:
    print(row["pnode_id"], row["pnode_name"], row["zone"])
