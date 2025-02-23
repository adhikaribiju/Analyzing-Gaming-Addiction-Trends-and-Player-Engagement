import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

columns = [
    'game_id', 'title', 'developer', 'publisher', 'genre', 'release_date',
    'platforms', 'multiplayer_support', 'graphics_quality', 'story_depth',
    'DLC_count', 'max_concurrent_players', 'positive_review_pct',
    'average_review_score', 'review_sentiment_score', 'number_of_reviews'
]

app_list_url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
app_list_response = requests.get(app_list_url)
app_list_data = app_list_response.json()


apps = app_list_data['applist']['apps']
app_ids = [str(app['appid']) for app in apps][:100000]


# set up session
session = requests.Session()
retry = Retry(connect=5, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

# store game data
all_games_data = []

for idx, app_id in enumerate(app_ids):
    try:
        url = f'http://store.steampowered.com/api/appdetails?appids={app_id}'
        response = session.get(url, timeout=10)
        response.raise_for_status()
        game_data = response.json()
        
        if game_data.get(app_id) and game_data[app_id]['success']:
            data = game_data[app_id]['data']
            
            filtered_data = {
                'game_id': data.get('steam_appid'),
                'title': data.get('name'),
                'developer': ', '.join(data.get('developers', [])) if data.get('developers') else 'Unknown',
                'publisher': ', '.join(data.get('publishers', [])) if data.get('publishers') else 'Unknown',
                'genre': ', '.join([genre['description'] for genre in data.get('genres', [])]) if data.get('genres') else 'N/A',
                'release_date': data.get('release_date', {}).get('date') if isinstance(data.get('release_date'), dict) else 'TBA',
                'platforms': ', '.join([k for k, v in data.get('platforms', {}).items() if v]) if data.get('platforms') else 'Unknown',
                'multiplayer_support': 'Multi-player' in [category['description'] for category in data.get('categories', [])] if data.get('categories') else False,
                'DLC_count': len(data.get('dlc', [])) if data.get('dlc') else 0,
                'max_concurrent_players': data.get('recommendations', {}).get('total', 0) if data.get('recommendations') else 0,
                'positive_review_pct': data.get('metacritic', {}).get('score', 0) if data.get('metacritic') else 0,
                'average_review_score': data.get('metacritic', {}).get('score', 0) if data.get('metacritic') else 0,
                'review_sentiment_score': data.get('metacritic', {}).get('score', 0) if data.get('metacritic') else 0,
                'number_of_reviews': data.get('recommendations', {}).get('total', 0) if data.get('recommendations') else 0,
                'graphics_quality': 'High' if '4K' in data.get('short_description', '') else 'Standard',
                'story_depth': 'Deep' if 'story' in data.get('short_description', '').lower() else 'Light'
            }

            # get Max Concurrent Players
            max_players_url = f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app_id}'
            max_players_response = requests.get(max_players_url, timeout=10)

            if max_players_response.status_code == 200:
                max_players_data = max_players_response.json()
                filtered_data['max_concurrent_players'] = max_players_data.get('response', {}).get('player_count', 0)
            else:
                print(f"Failed to fetch max players for App ID {app_id}: Status Code {max_players_response.status_code}")
                filtered_data['max_concurrent_players'] = 0

            all_games_data.append(filtered_data)
        
        print(f"Fetched data for App ID {app_id} ({idx + 1}/{len(app_ids)})")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for App ID {app_id}: {e}")
    
    time.sleep(0.5)
        


df = pd.DataFrame(all_games_data, columns=columns)


df.to_csv('games_data.csv', index=False)

print("Data collection complete. Saved to 'games_data.csv'")

