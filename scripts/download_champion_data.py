
import json
import requests
import os

# Create a directory to store the champion data
if not os.path.exists("champion_data"):
    os.makedirs("champion_data")

with open("champion.json", "r") as f:
    data = json.load(f)

champion_names = data["data"].keys()

for champion_name in champion_names:
    url = f"https://ddragon.leagueoflegends.com/cdn/15.20.1/data/en_US/champion/{champion_name}.json"
    response = requests.get(url)
    with open(f"champion_data/{champion_name}.json", "w") as f:
        f.write(response.text)
    print(f"Downloaded {champion_name}.json")

print("All champion data downloaded.")
