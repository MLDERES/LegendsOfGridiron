import json
import requests
from config import DATA_FOLDER
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

BASE_URI = 'https://api.sleeper.app/v1/'
PLAYERS_URI = BASE_URI + 'players/nfl'
LEAGUE_URI = BASE_URI + 'league'
LEAGUE_ID = os.getenv('SLEEPER_LEAGUE_ID')
DRAFT_ID = os.getenv('DRAFT_ID_2024')

# Get all players from sleeper
def get_all_players():
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    players = r.json()
    with open(DATA_FOLDER/'players.json', 'w') as file:
        json.dump(players, file)
    return players

# Get all rosters from sleeper
def get_all_rosters(leauge_id):
    r = requests.get(f'{LEAGUE_URI}/{leauge_id}/rosters')
    rosters = r.json()
    with open(DATA_FOLDER/'rosters.json', 'w') as file:
        json.dump(rosters, file)
    return rosters

# Get roster by owner from sleeper
def get_roster_by_owner(owner):
    rosters = get_all_rosters()
    for roster in rosters:
        if roster['owner_id'] == owner:
            return roster
    return None

# Get users in a league
def get_users_in_league(leauge_id):
    r = requests.get(f'{LEAGUE_URI}/{leauge_id}/users')
    users = r.json()
    with open(DATA_FOLDER/'users.json', 'w') as file:
        json.dump(users, file)
    return users

# Get all picks in a draft
def get_all_picks(draft_id):
    r = requests.get(f'{BASE_URI}/draft/{draft_id}/picks')
    drafts = r.json()
    with open(DATA_FOLDER/'draft_picks.json', 'w') as file:
        json.dump(drafts, file)
    
    # Load the draft picks data into a dataframe
    draft_picks = pd.read_json(DATA_FOLDER/'draft_picks.json')

    # Expand the metadata column into separate columns
    draft_picks = pd.concat([draft_picks.drop(['metadata'], axis=1), draft_picks['metadata'].apply(pd.Series)], axis=1)
    draft_picks['Player Fullname'] = draft_picks['first_name'] + ' ' + draft_picks['last_name']
    draft_picks.to_csv(DATA_FOLDER/'draft_picks.csv', index=False)
        
    return draft_picks

if __name__ == '__main__':
   get_all_picks()