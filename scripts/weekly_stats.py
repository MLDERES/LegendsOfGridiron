# Get all the players from Sleeper and store the pertinent information in a SQLite database
import requests
import sqlite3
import json
from sleeper import get_all_players, get_users_in_league, get_all_rosters, get_matchups
from manage import clean_player_data
from config import LEAGUE_LIST
import pandas as pd
from utility import run_query_scalar, run_query, DATA_PATH
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEBUG= logger.debug
INFO = logger.info

SLEEPER_API = "https://api.sleeper.app/v1/players/nfl"

def update_weekly_matchups(week = 1, drop_table = False):
    conn = sqlite3.connect(DATA_PATH/'league_db.db')
    if drop_table:
        conn.execute("DROP TABLE IF EXISTS matchups")
    
    def update_matchups(league_id, week):
        df_matchup = get_matchups(league_id, week)
        df_matchup[['league_id','week']] = league_id, week
        df_matchup = df_matchup[['league_id','week','points','roster_id','matchup_id']]
        #print(df_matchup)
        df_matchup.to_sql('matchups', conn, if_exists='append', index=False)
        
    # For each league
    for league in LEAGUE_LIST:
        league_id = LEAGUE_LIST[league]
        if drop_table:
            for w in range(1, week + 1):
                update_matchups(league_id, w)
        else:
            update_matchups(league_id, week)
        
    conn.close()       
    
def calculate_standings(df_results):
    # Since we have all the results, let's calculate the standings
    # The format of the file is League, Weeek, Winner, Loser, Winner Pts, Loser Pts
    # First get the results by league
    for l in df_results.League.unique():
        INFO(f"Calculating Standings for {l}")
        df = df_results[df_results.League == l]
        # Total the Points for and the points against by team, but also the points if they were the loser   
        winner_points = df.groupby('Winner')['Winner Pts'].sum().reset_index().rename(columns={'Winner': 'Team', 'Winner Pts': 'Total Points'})
        loser_points = df.groupby('Loser')['Loser Pts'].sum().reset_index().rename(columns={'Loser': 'Team', 'Loser Pts': 'Total Points'})
        
        # Combine the points from winners and losers
        total_points_df = pd.concat([winner_points, loser_points]).groupby('Team').sum().reset_index().sort_values(by='Total Points', ascending=False)
        total_points_df['Total Points'] = round(total_points_df['Total Points'],2)
        # Now get the number of times each team has won in the league
        df_wins = df.groupby('Winner').size().reset_index(name='Wins')
        # Now get the number of times each team has lost in the league
        df_losses = df.groupby('Loser').size().reset_index(name='Losses')
        # combine the two dataframes
        df_wins = df_wins.set_index('Winner')
        df_losses = df_losses.set_index('Loser')
        df_wins = df_wins.join(df_losses, how='outer')
        # Join the total points
        df_wins = df_wins.join(total_points_df.set_index('Team'), how='outer')
        # fill in the missing values
        df_wins = df_wins.fillna(0)
        # calculate the win percentage
        df_wins['Win_Percentage'] = round(df_wins['Wins'] / (df_wins['Wins'] + df_wins['Losses']),2)
        # Sort by win percentage
        df_wins = df_wins.sort_values('Win_Percentage', ascending=False)
        # filter out "MEDIAN"
        df_wins = df_wins[df_wins.index != 'MEDIAN']
        
        league_name = l.replace(' ','_')
        df_wins.to_csv(DATA_PATH/f'standings/league_{league_name}.csv', index=True, index_label='Team')
    
    
    
if __name__ == '__main__':
    latest_week = run_query_scalar("select max(week) from matchups")+1
    INFO(f'Updating matchups for week {latest_week}')
    update_weekly_matchups(latest_week, drop_table=True)

    df_outcomes = run_query('''
    SELECT r1.league_name, m1.week, r1.coach_name as 'Winner', r2.coach_name as 'Loser', m1.points, m2.points
        FROM matchups m1 
        JOIN matchups m2 on m1.matchup_id = m2.matchup_id and m1.week = m2.week and m1.league_id = m2.league_id and m1.roster_id != m2.roster_id
        JOIN roster_coaches r1 on m1.roster_id = r1.roster_id and m1.league_id = r1.league_id
        JOIN roster_coaches r2 on m2.roster_id = r2.roster_id and m2.league_id = r2.league_id
        WHERE m1.points > m2.points''', 
        cols=['League','Week','Winner','Loser','Winner Pts','Loser Pts'])
    # Calculate the median for each league
    INFO('Calculating median points')
    df_median_points = run_query('''select league_id, week, points from matchups''').groupby(['league_id','week']).median().reset_index()

    df_team_points = run_query('''
    SELECT r.league_id, r.league_name, m.week, m.roster_id, r.coach_name, m.points 
    FROM matchups m 
        JOIN roster_coaches r on m.roster_id = r.roster_id and m.league_id = r.league_id''')

    df_team_points['league_id'] = df_team_points['league_id'].astype(int)

    df_combined = pd.merge(df_team_points, df_median_points, on=['league_id','week'], suffixes=('_team','_median'),how='inner')
    df_combined['Winner']=df_combined.apply(lambda row: row['coach_name'] if row['points_team']> row['points_median'] else 'MEDIAN', axis=1)
    df_combined['Loser']=df_combined.apply(lambda row: row['coach_name'] if row['points_team']<= row['points_median'] else 'MEDIAN', axis=1)
    df_output= df_combined[['league_name','week','Winner','Loser']].rename(columns={'league_name':'League','week':'Week'})
    df_results = pd.concat([df_outcomes,df_output], axis=0)
    INFO('Writing out the results')
    df_results.to_csv(DATA_PATH/'league_outcomes.csv', index=False)
    
    # Now update the standings
    INFO('Calculating Standings')
    calculate_standings(df_results)
