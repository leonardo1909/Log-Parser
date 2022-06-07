import pandas as pd
import re
import json


def matches_index(df):
    return df.loc[df["Description"].str.contains(" InitGame:")]

def kills_index(df):
    return df.loc[df["Description"].str.contains(" Kill:")]

def build_matches_kill_info(matches, kills, matches_list):
    for i in range(len(matches.index)):
        try:
            next_matche_index = matches.iloc[i+1]._name
        except IndexError:
            next_matche_index = None
        
        key = f"game_{i+1}"
        game = {
            key: {
            "total_kills": len(kills.loc[matches.iloc[i]._name:next_matche_index]),
            "players": [],
            "kills": {}
            }
        }

        for kill in kills.loc[matches.iloc[i]._name:next_matche_index].iterrows():
            dead = re.search(r'killed.(.*?)by', kill[1]["Description"]).group(1).strip()
            killer = re.search(r'[0-9]: (.*?)killed', kill[1]["Description"]).group(1).strip()
            
            if dead not in game[key]["players"]:
                game[key]["players"].append(dead)
            if killer not in game[key]["players"] and killer != "<world>":
                game[key]["players"].append(killer)

            if killer != "<world>":
                try:
                    game[key]["kills"][killer] += 1
                except KeyError:
                    game[key]["kills"][killer] = 1

                try:
                    game[key]["kills"][dead] -= 1
                except KeyError:
                    game[key]["kills"][dead] = -1
            else:
                try:
                    game[key]["kills"][dead] -= 1
                except KeyError:
                    game[key]["kills"][dead] = -1             

        matches_list.update(game)

file_name = "qgames.log"
file = open(file_name, "r")

matches_list = {}

df = pd.DataFrame([(line[:6], line[6:]) for line in file.readlines()])
df.columns = ['DateAndTime', 'Description']
df.head()

matches = matches_index(df)
kills = kills_index(df)

build_matches_kill_info(matches, kills, matches_list)

print(json.dumps(matches_list))
