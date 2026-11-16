#!/usr/bin/env python3

import pandas as pd
import requests

url = "https://api.jolpi.ca/ergast/f1/races/"

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()
races = data["MRData"]["RaceTable"]["Races"]
df = pd.json_normalize(races)

print(df.columns)