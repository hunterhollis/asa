# Dependencies
import requests
import json
import pandas as pd
import time
from creds import geoapify_key, postgresql_pw
from sqlalchemy import create_engine

# import existing venue info from xlsx
team_venues = pd.read_excel('data\\team_venue_info.xlsx')

# target addresses
addresses = team_venues['full_address']
urls = []

# Build the endpoint URLs
for address in addresses:
    target_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&format=json&apiKey={geoapify_key}"
    urls.append(target_url)

# lists to hold latitudes and longitudes
lats = []
lons = []

# Run a request to endpoint and convert result to json
start_time = time.time()

for i in range(len(urls)):
    geo_data = requests.get(urls[i]).json()
    try:
        lat = geo_data["results"][0]["lat"]
        lon = geo_data["results"][0]["lon"]
    except (KeyError, IndexError) as e:
        print(f"Error: no results in line {i}")
        print(e)
        lat = 0
        lon = 0
    lats.append(lat)
    lons.append(lon)
    if (i+1) % 25 == 0:
        print(f"URL #{i+1} complete")
    elif i == (len(urls)-1):
        print("Done!")

run_time = int(time.time() - start_time)
print(f"Run time: {run_time} seconds")

# Print length of lat and lon lists
print(f"\nLats: {len(lats)}")
print(f"Lons: {len(lons)}")

# update DataFrame
team_venues['lat'] = lats
team_venues['lon'] = lons

# create postgresql connection
engine = create_engine(f'postgresql+psycopg2://postgres:{postgresql_pw}@localhost:5432/api_sports')

# import team_venues to new table in api-sports db
team_venues.to_sql('team_venues', con=engine, if_exists='replace', index=False)

print(f'\nTeam venues uploaded to team_venues table.')