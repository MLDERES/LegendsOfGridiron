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
def get_all_players(save=False):
    r = requests.get('https://api.sleeper.app/v1/players/nfl')
    players = r.json()
    if save:
        with open(DATA_FOLDER/'players.json', 'w') as file:
            json.dump(players, file)
    return players

# Get all rosters from sleeper
def get_all_rosters(league_id, save=False):
    r = requests.get(f'{LEAGUE_URI}/{league_id}/rosters')
    rosters = r.json()
    if save:
        with open(DATA_FOLDER/'rosters.json', 'w') as file:
            json.dump(rosters, file)
    rosters_df = pd.DataFrame(rosters)
    return rosters_df

# Get roster by owner from sleeper
def get_roster_by_owner(owner):
    rosters = get_all_rosters()
    for roster in rosters:
        if roster['owner_id'] == owner:
            return roster
    return None

# Get users in a league
def get_users_in_league(league_id, save = False):
    r = requests.get(f'{LEAGUE_URI}/{league_id}/users')
    users = r.json()
    if save: 
        with open(DATA_FOLDER/'users.json', 'w') as file:
            json.dump(users, file)
        users_df = pd.read_json(DATA_FOLDER/'users.json')
    else:
        users_df = pd.DataFrame(users)
    # Expand the metadata column into separate columns
    users_df = pd.concat([users_df.drop(['metadata'], axis=1), users_df['metadata'].apply(pd.Series)], axis=1)
    
    # Remove unnecessary columns
    users_df = users_df.drop(columns=['settings','is_bot','user_message_pn', 'transaction_waiver',
       'transaction_trade', 'transaction_free_agent',
       'transaction_commissioner', 'trade_block_pn','player_nickname_update', 'player_like_pn', 'mention_pn',
       'mascot_message', 'league_report_pn', 'archived', 'allow_pn','avatar'],errors='ignore')
    return users_df

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

# Get the matchups for the week in a given week
def get_matchups(league_id, week):
    r = requests.get(f'{LEAGUE_URI}/{league_id}/matchups/{week}')
    matchups = r.json()
   
    # Load the matchups data into a dataframe
    matchups_df = pd.DataFrame(matchups)
    return matchups_df

if __name__ == '__main__':
   mu = get_matchups(1060410179696533504, 1)
   print(mu)