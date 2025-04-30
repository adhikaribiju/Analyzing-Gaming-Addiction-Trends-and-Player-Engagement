import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load game IDs from CSV
game_ids_df = pd.read_csv("game_id.csv")  # feed the game ids from the gamedatacollections result
game_ids = game_ids_df['game_id'].tolist()

# Set up session with retry strategy
session = requests.Session()
retry = Retry(connect=5, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

# Define the desired review columns
review_columns = [
    'game_id', 'recommendationid', 'review', 'timestamp_created',
    'voted_up', 'votes_up', 'votes_funny', 'steam_purchase',
    'received_for_free', 'written_during_early_access',
    'playtime_forever', 'playtime_last_two_weeks'
]

# Store review data
all_reviews = []

# Loop through each game ID to fetch reviews
for idx, game_id in enumerate(game_ids):
    try:
        url = f"https://store.steampowered.com/appreviews/{game_id}?json=1&language=en&filter=recent&day_range=30&review_type=all&purchase_type=steam"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        review_data = response.json()

        if 'reviews' in review_data:
            for review in review_data['reviews']:
                review_entry = {
                    'game_id': game_id,
                    'recommendationid': review.get('recommendationid'),
                    'review': review.get('review', ''),
                    'timestamp_created': review.get('timestamp_created'),
                    'voted_up': review.get('voted_up'),
                    'votes_up': review.get('votes_up', 0),
                    'votes_funny': review.get('votes_funny', 0),
                    'steam_purchase': review.get('steam_purchase', False),
                    'received_for_free': review.get('received_for_free', False),
                    'written_during_early_access': review.get('written_during_early_access', False),
                    'playtime_forever': review.get('author', {}).get('playtime_forever', 0),
                    'playtime_last_two_weeks': review.get('author', {}).get('playtime_last_two_weeks', 0)
                }
                all_reviews.append(review_entry)

        print(f"Fetched reviews for Game ID {game_id} ({idx + 1}/{len(game_ids)})")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching reviews for Game ID {game_id}: {e}")
   
    # Small delay to avoid rate limits
    time.sleep(0.5)

# Convert to DataFrame
reviews_df = pd.DataFrame(all_reviews, columns=review_columns)

# Save to CSV
reviews_df.to_csv('reviews.csv', index=False)

print("Review data collection complete. Saved to 'reviews.csv'")