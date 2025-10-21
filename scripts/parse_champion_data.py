
import json
import os
import csv

# Open the CSV file for writing
with open("champion_abilities.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Champion", "Ability Type", "Ability Name", "Description"])

    # Iterate over the files in the champion_data directory
    for filename in os.listdir("champion_data"):
        if filename.endswith(".json"):
            with open(os.path.join("champion_data", filename), "r") as f:
                data = json.load(f)
                
                # The champion name is the key in the data dictionary
                champion_name = list(data["data"].keys())[0]
                champion_data = data["data"][champion_name]

                # Get the passive ability
                passive = champion_data["passive"]
                writer.writerow([champion_name, "Passive", passive["name"], passive["description"]])

                # Get the spells
                for spell in champion_data["spells"]:
                    ability_type = ""
                    if spell["id"].endswith("Q"):
                        ability_type = "Q"
                    elif spell["id"].endswith("W"):
                        ability_type = "W"
                    elif spell["id"].endswith("E"):
                        ability_type = "E"
                    elif spell["id"].endswith("R"):
                        ability_type = "Ultimate"
                    writer.writerow([champion_name, ability_type, spell["name"], spell["description"]])

print("CSV file created successfully.")
