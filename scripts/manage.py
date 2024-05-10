import pandas as pd
from config import DATA_FOLDER

# Determine the ADP to draft position for each player in the database

# Calculate the difference between the pick and the player's ADP
def correlate_data():
    # Load the full ranking data into a dataframe
    full_ranking = pd.read_csv(DATA_FOLDER/'full_ranking.csv')
    
    # Load the draft picks data into a dataframe
    draft_picks = pd.read_json(DATA_FOLDER/'draft_picks.json')


    # Expand the metadata column into separate columns
    draft_picks = pd.concat([draft_picks.drop(['metadata'], axis=1), draft_picks['metadata'].apply(pd.Series)], axis=1)
    print(draft_picks.columns)

correlate_data()    

    