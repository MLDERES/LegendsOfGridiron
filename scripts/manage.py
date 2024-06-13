import pandas as pd
from config import DATA_FOLDER
import json

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

def clean_player_data():
    # Read the JSON data from a file
    with open(DATA_FOLDER/'players.json', 'r') as file:
        data = json.load(file)

    # Convert the JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')

    # Remove the brackets from the fantasy_positions column
    df['fantasy_positions'] = df['fantasy_positions'].apply(lambda x: x[0] if isinstance(x, list) and x else x)

    # Filter the DataFrame to include only players with positions WR, QB, RB, TE
    filtered_df = df[df['position'].isin(['WR', 'QB', 'RB', 'TE'])]

    # Save the filtered DataFrame to a CSV file
    filtered_df.to_csv(DATA_FOLDER/'nfl_players_filtered.csv', index=False)

    # Print a success message
    print("Filtered data has been saved to 'nfl_players_filtered.csv'.")

# After getting the data from sleeper (the users in the league)
def clean_league_user_data(league_user_json_data):
    # Convert JSON data to DataFrame
    df = pd.DataFrame(league_user_json_data)

    # Extract the team_name from metadata
    df['team_name'] = df['metadata'].apply(lambda x: x.get('team_name') if isinstance(x, dict) else None)

    # Filter the DataFrame to include only the specified columns
    filtered_df = df[['user_id', 'league_id', 'display_name', 'team_name']]
    
    return filtered_df

    