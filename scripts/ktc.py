from config import DATA_FOLDER
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

# Get rankings from KTC
def get_rankings(page):
    r = requests.get(f'https://keeptradecut.com/fantasy-rankings?page={page}&filters=QB|WR|RB|TE&format=2')
    rankings = r.text
    with open(DATA_FOLDER/'rankings_{page}.html', 'w') as file:
        file.write(rankings)
    return rankings

def parse_rankings(page):
    with open(DATA_FOLDER/'rankings_{page}.html', 'r') as file:
        rankings = file.read()
    
    soup = BeautifulSoup(rankings, 'html.parser')
    players = soup.find_all('div', class_='onePlayer')
    player_data = []
    
    # Extract info for each player
    # Extract information for each player
    for player in players:
        rank = player.find('div', class_='rank-number').p.text.strip()
        name = player.find('div', class_='player-name').a.text.strip()
        team = player.find('span', class_='player-team').text.strip()
        position = player.find('p', class_='position').text.strip()
        value = player.find('div', class_='value').p.text.strip()

        # Append to list
        player_data.append({
            'Rank': rank,
            'Name': name,
            'Position': position,
            'Team': team,
            'Value': value
        })

    # Create DataFrame
    df = pd.DataFrame(player_data)
    return df
    
def do_work():
    # Get the rankings for all 5 pages of data
    all_rankings = []
    for page in range(6):
        get_rankings(page)
        ranking = parse_rankings(page)
        all_rankings.append(ranking)
        ranking.to_csv(DATA_FOLDER/f'ranking_{page}.csv',index=False)
    full_ranking = pd.concat(all_rankings)
    full_ranking.to_csv(DATA_FOLDER/'full_ranking.csv', index=False)
    
if __name__ == '__main__':
    do_work()