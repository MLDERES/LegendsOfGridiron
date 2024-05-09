import json
import requests
from config import DATA_FOLDER
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URI = 'https://api.sleeper.app/v1/'
PLAYERS_URI = BASE_URI + 'players/nfl'
LEAGUE_URI = BASE_URI + 'league'
LEAGUE_ID = os.getenv('SLEEPER_LEAGUE_ID')

# Get all players from sleeper
def get_all_players():
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    players = r.json()
    with open(DATA_FOLDER/'players.json', 'w') as file:
        json.dump(players, file)
    return players

# Get all rosters from sleeper
def get_all_rosters():
    r = requests.get(f'{LEAGUE_URI}/{LEAGUE_ID}/rosters')
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
def get_users_in_league():
    r = requests.get(f'{LEAGUE_URI}/{LEAGUE_ID}/users')
    users = r.json()
    with open(DATA_FOLDER/'users.json', 'w') as file:
        json.dump(users, file)
    return users

if __name__ == '__main__':
    get_users_in_league()