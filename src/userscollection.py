import requests
import pandas as pd
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Generate random Steam User IDs (these are not guaranteed to be valid)
def generate_random_steam_ids(n=50000):
    # SteamID64 range (valid SteamID64 values generally start from 76561197960265728)
    base_id = 76561197960265728
    return [str(base_id + random.randint(0, 1000000000)) for _ in range(n)]

# columns for the output CSV
columns = ['user_id', 'game_count', 'appid', 'name', 'playtime_forever', 'playtime_2weeks']

# Generate 50,000 random Steam User IDs
user_ids = generate_random_steam_ids()


session = requests.Session()
retry = Retry(connect=5, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)


API_KEY = 'API_KEY' # removing this for privacy

# Store user game data
all_user_data = []

# Fetch data for each random user
for idx, user_id in enumerate(user_ids):
    try:
        url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={user_id}&include_appinfo=true&include_played_free_games=true'
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']
            game_count = data['response'].get('game_count', 0)
            for game in games:
                game_data = {
                    'user_id': user_id,
                    'game_count': game_count,
                    'appid': game.get('appid'),
                    'name': game.get('name', 'Unknown'),
                    'playtime_forever': game.get('playtime_forever', 0),
                    'playtime_2weeks': game.get('playtime_2weeks', 0)
                }
                all_user_data.append(game_data)
        
        print(f'Fetched data for User ID {user_id} ({idx + 1}/{len(user_ids)})')
        
    except requests.exceptions.RequestException as e:
        print(f'Error fetching data for User ID {user_id}: {e}')

    # rate limiting
    time.sleep(0.5)


df = pd.DataFrame(all_user_data, columns=columns)

df.to_csv('user_playtime_data.csv', index=False)

print('Data collection complete. Saved to "user_playtime_data.csv"')
