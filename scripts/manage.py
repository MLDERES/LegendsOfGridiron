import pandas as pd
from config import DATA_FOLDER
import json
import sqlite3

# Determine the ADP to draft position for each player in the database

# Calculate the difference between the pick and the player's ADP
def correlate_data():
    # Load the full ranking data into a dataframe
    full_ranking = pd.read_csv(DATA_FOLDER/'full_ranking.csv')
    
    # Expand the metadata column into separate columns
    draft_picks = pd.concat([draft_picks.drop(['metadata'], axis=1), draft_picks['metadata'].apply(pd.Series)], axis=1)
    draft_picks['Player Fullname'] = draft_picks['first_name'] + ' ' + draft_picks['last_name']
    draft_picks.to_csv(DATA_FOLDER/'draft_picks.csv', index=False)
    
    print(draft_picks.columns)

def clean_player_data(data):
    if data is None:
        # Read the JSON data from a file
        with open(DATA_FOLDER/'players.json', 'r') as file:
            data = json.load(file)

    # Convert the JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')

    # Remove the brackets from the fantasy_positions column
    df['fantasy_positions'] = df['fantasy_positions'].apply(lambda x: x[0] if isinstance(x, list) and x else x)

    # Filter the DataFrame to include only players with positions WR, QB, RB, TE
    filtered_df = df[df['position'].isin(['WR', 'QB', 'RB', 'TE'])]
    # Drop unnecessary columns
    filtered_df = filtered_df.drop(columns=['injury_status','birth_country',
       'birth_city', 'injury_start_date', 'birth_state','competitions','rotowire_id', 'sportradar_id', 'injury_notes',
       'yahoo_id', 'news_updated', 'injury_body_part',
       'metadata','high_school'])
    # Set the index to player_id
    filtered_df = filtered_df.set_index('player_id')
    return filtered_df

# After getting the data from sleeper (the users in the league)
def clean_league_user_data(league_user_json_data):
    # Convert JSON data to DataFrame
    df = pd.DataFrame(league_user_json_data)

    # Extract the team_name from metadata
    df['team_name'] = df['metadata'].apply(lambda x: x.get('team_name') if isinstance(x, dict) else None)

    # Filter the DataFrame to include only the specified columns
    filtered_df = df[['user_id', 'league_id', 'display_name', 'team_name']]
    
    return filtered_df

def update_db_with_players(player_df):
    # Create a connection to the database
    conn = sqlite3.connect('../data/league_db.db')

    # Insert the data into the database
    player_df.to_sql('players', conn, if_exists='replace', index=True)

def weekly_maintenance():
    # Get player data
    # Insert player data into the database
    # Get all the coaches in the leagues
    # Insert coaches into the database
    pass