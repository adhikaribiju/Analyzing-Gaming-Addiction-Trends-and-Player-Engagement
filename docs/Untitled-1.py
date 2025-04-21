


# Removing rows with any missing values
games_data.dropna(inplace=True)


# Attemptting to parse the dates with possible date formats : 
# Possible formats known from: https://steamcommunity.com/sharedfiles/filedetails/?id=2554483179#:~:text=Date%20part%20order%20can%20be,format%20will%20be%20applied%20immediately.

valid_dates_format1 = pd.to_datetime(games_data['release_date'], format='%d %b, %Y', errors='coerce')
valid_dates_format2 = pd.to_datetime(games_data['release_date'], format='%b %d, %Y', errors='coerce')
valid_dates_format3 = pd.to_datetime(games_data['release_date'], format='%d %b %Y', errors='coerce')

# Identify rows that do not match either of the formats
invalid_dates = games_data[(valid_dates_format1.isna()) & (valid_dates_format2.isna()) & (valid_dates_format3.isna())]

# let's remove those invalid dates
invalid_dates_list = invalid_dates['release_date'].tolist()
games_data = games_data[~games_data['release_date'].isin(invalid_dates_list)]


# Combining all parsed dates
games_data['release_date'] = valid_dates_format1.fillna(valid_dates_format2).fillna(valid_dates_format3)

# Convert dates to 'YYYY-MM-DD' format for consistency only
games_data['release_date'] = games_data['release_date'].dt.strftime('%Y-%m-%d')


# Rename the column from 'appid' to 'game_id'
users_data.rename(columns={'appid': 'game_id'}, inplace=True)

# let's add avg_playtime coloumn - for viz
users_data['avg_playtime'] = users_data['playtime_2weeks'] / 14

# Convert playtime from minutes to hours
users_data['playtime_2weeks'] = users_data['playtime_2weeks'] / 60
users_data['playtime_forever'] = users_data['playtime_forever'] / 60



# Q1
# let's first filter only active users
active_users = users_data[users_data['playtime_2weeks'] > 0]

# calculate weekly playtime (in hours) for those active uses
active_users['weekly_playtime_hours'] = (active_users['playtime_2weeks'] / 2)


# visualization the  distribution of weekly playtime
plt.figure(figsize=(8, 6))
plt.hist(active_users['weekly_playtime_hours'], bins=30, color='skyblue', edgecolor='black')
plt.axvline(x=20, color='red', linestyle='--', label='Addiction Threshold (20 hours)')
plt.xlabel('Average Weekly Playtime (Hours)')
plt.ylabel('Number of Active Users')
plt.title('Distribution of Weekly Playtime Among Active Users')
plt.legend()
plt.grid(True)
plt.show()



# Lets also cateogrize active users based on weekly playtime
def categorize_playtime(hours):
    if hours < 7:
        return 'Casual Gamer'
    elif hours < 20:
        return 'Moderate Gamer'
    else:
        return 'Potential Addiction'

active_users['playtime_category'] = active_users['weekly_playtime_hours'].apply(categorize_playtime)

# total active users in each category
active_category_counts = active_users['playtime_category'].value_counts()
print("\nActive User Distribution by Playtime Category:")
print(active_category_counts)

plt.figure(figsize=(6, 6))
plt.pie(active_category_counts, labels=active_category_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66c2a5', '#fc8d62', '#8da0cb'])
plt.title('Active User Distribution by Playtime Category')
plt.show()

plt.figure(figsize=(8, 5))
active_category_counts.plot(kind='bar', color=['#66c2a5', '#fc8d62', '#8da0cb'], edgecolor='black')

# Labels and title
plt.xlabel('Playtime Category')
plt.ylabel('Number of Users')
plt.title('Active User Distribution by Playtime Category')
plt.xticks(rotation=0)  # Keep category labels horizontal
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()



#Q2.

# Merging user_data with games_data on game_id
merged_data = users_data.merge(games_data, on='game_id', how='left')
merged_data.dropna(inplace=True)


merged_data = merged_data[merged_data['playtime_2weeks'] > 0]


merged_data['multiplayer_support'] = merged_data['multiplayer_support'].astype(int)


# game design elements for analysis
design_elements = ["DLC_count", "multiplayer_support", "max_concurrent_players", "average_review_score"]


merged_data['playtime_forever'] = np.log1p(merged_data['playtime_forever'])
merged_data['DLC_count'] = np.log1p(merged_data['DLC_count'])
merged_data['max_concurrent_players'] = np.log1p(merged_data['max_concurrent_players'])
merged_data['average_review_score'] = np.log1p(merged_data['average_review_score'])
merged_data['playtime_2weeks'] = np.log1p(merged_data['playtime_2weeks'])

correlation_results = merged_data[["playtime_forever"] + design_elements].corr()


# heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_results, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Between Game Design Elements and Playtime")
plt.show()



#hyopthesis testing
import pandas as pd
from scipy.stats import chi2_contingency

merged_data = users_data.merge(games_data, on='game_id', how='left')
merged_data.dropna(inplace=True)

merged_data = merged_data[merged_data['playtime_2weeks'] > 0]
merged_data['multiplayer_support'] = merged_data['multiplayer_support'].astype(int)


df_filtered = merged_data[merged_data['playtime_2weeks'] > 0].copy()

# Create addicted column: 1 if playtime_2weeks > 20, else 0
df_filtered['addicted'] = (df_filtered['playtime_2weeks'] > 40).astype(int)

# Create contingency table between multiplayer_support and addicted status
contingency_table = pd.crosstab(df_filtered['multiplayer_support'], df_filtered['addicted'])

print("Contingency Table:")
print(contingency_table)

# Perform the chi-square test
chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"\nChi-square Statistic: {chi2:.4f}")
print(f"Degrees of Freedom: {dof}")
print(f"P-value: {p}")


prop_df = df_filtered.groupby('multiplayer_support')['addicted'].mean().reset_index()
prop_df['Game Type'] = prop_df['multiplayer_support'].map({0: 'Single-player', 1: 'Multiplayer'})

plt.figure(figsize=(8, 5))
sns.barplot(x='Game Type', y='addicted', data=prop_df)
plt.ylabel("Proportion of Addicted Players")
plt.title("Proportion of Addicted Players by Game Type")

plt.ylim(0, 0.3) 
plt.show()

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from scipy.stats import ttest_ind


merged_data = users_data.merge(games_data, on='game_id', how='left')
merged_data.dropna(inplace=True)

merged_data = merged_data[merged_data['playtime_2weeks'] > 0]

merged_data['multiplayer_support'] = merged_data['multiplayer_support'].astype(int)


# Assume df_filtered is defined as before with an 'addicted' column
df_filtered = merged_data[merged_data['playtime_2weeks'] > 0].copy()
df_filtered['addicted'] = (df_filtered['playtime_2weeks'] > 40).astype(int)

# Define groups
group_addicted = df_filtered[df_filtered['addicted'] == 1]
group_non_addicted = df_filtered[df_filtered['addicted'] == 0]

# Function to run and print t-test results for a given predictor
def run_ttest(predictor):
    t_stat, p_value = ttest_ind(group_addicted[predictor], group_non_addicted[predictor], nan_policy='omit')
    print(f"T-test for {predictor}:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}\n")

# Run t-tests for each predictor
run_ttest('DLC_count')
run_ttest('max_concurrent_players')
run_ttest('average_review_score')







# Q3


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr


# Merge user data with game data
merged_data = users_data.merge(games_data, on="game_id", how="inner")

merged_data = merged_data[merged_data['playtime_2weeks'] > 40]

genre_playtime = merged_data.groupby("genre")["playtime_2weeks"].sum().sort_values(ascending=False)

# Plot genre vs. total playtime
plt.figure(figsize=(12, 6))
sns.barplot(x=genre_playtime.index[:10], y=genre_playtime.values[:10])
plt.xticks(rotation=30, ha="right")  # Rotating labels for better readability
plt.xlabel("Game Genre")
plt.ylabel("Total Playtime (hours)")
plt.title("Top 10 Most Engaging Game Genres for addicted users by Playtime")
plt.tight_layout()  # Adjust layout to prevent clipping
plt.show()

addiction_correlation, _ = pearsonr(merged_data["playtime_forever"], merged_data["average_review_score"])


# -----------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr


# Merge user data with game data
merged_data = users_data.merge(games_data, on="game_id", how="inner")

merged_data = merged_data[merged_data['playtime_2weeks'] > 0]

merged_data = merged_data[merged_data['playtime_2weeks'] < 40]

genre_playtime = merged_data.groupby("genre")["playtime_2weeks"].sum().sort_values(ascending=False)

# Plot genre vs. total playtime
plt.figure(figsize=(12, 6))
sns.barplot(x=genre_playtime.index[:10], y=genre_playtime.values[:10])
plt.xticks(rotation=30, ha="right")  # Rotating labels for better readability
plt.xlabel("Game Genre")
plt.ylabel("Total Playtime (hours)")
plt.title("Top 10 Most Engaging Game Genres for non-addicted users by Playtime")
plt.tight_layout()  # Adjust layout to prevent clipping
plt.show()

addiction_correlation, _ = pearsonr(merged_data["playtime_forever"], merged_data["average_review_score"])




#Q4

merged_data = users_data.merge(games_data, on='game_id', how='left')
merged_data.dropna(inplace=True)

# get the title from the games_data
df_reviews = merged_data.merge(reviews_data, on='game_id', how='inner')

import re
import matplotlib.pyplot as plt
from textblob import TextBlob


df_reviews = df_reviews[df_reviews['playtime_2weeks'] > 0]

df_reviews = df_reviews[df_reviews['playtime_2weeks'] < 40]


#df_reviews= reviews_data

# Function to clean review text
def clean_text(text):
    if pd.isna(text):
        return ""
    text = re.sub(r"\[.*?\]", "", text)  # Removing tags like [h1], [b], etc.
    text = re.sub(r"http\S+|www\S+", "", text)  # Removng URLs
    text = re.sub(r"[^a-zA-Z0-9.,!?'\s]", "", text)  # Remove special characters
    text = text.lower().strip()  # Convert to lowercase and strip spaces
    return text

# Apply text cleaning
df_reviews["cleaned_review"] = df_reviews["review"].apply(clean_text)

# Function to get sentiment polarity
def get_sentiment(text):
    if not text:  # If empty text, return neutral
        return 0  
    return TextBlob(text).sentiment.polarity

# Apply sentiment analysis to the cleaned reviews
df_reviews["sentiment_score"] = df_reviews["cleaned_review"].apply(get_sentiment)

# Classify reviews based on sentiment score
df_reviews["sentiment"] = df_reviews["sentiment_score"].apply(
    lambda x: "Positive" if x > 0.05 else ("Negative" if x < -0.05 else "Neutral")
)

# Count of each sentiment category
sentiment_counts = df_reviews["sentiment"].value_counts()

# Visualization: Sentiment Distribution
plt.figure(figsize=(8, 5))
plt.bar(sentiment_counts.index, sentiment_counts.values)
plt.xlabel("Sentiment Category")
plt.ylabel("Number of Reviews")
plt.title("Distribution of Sentiments in Reviews(non-addicted)")
plt.show()

# sentiment by game
game_sentiment = df_reviews.groupby("title")["sentiment_score"].mean().reset_index()

# Top 10 most positively reviewed games
top_positive_games = game_sentiment.sort_values(by="sentiment_score", ascending=False).head(10)

# Top 10 most negatively reviewed games
top_negative_games = game_sentiment.sort_values(by="sentiment_score", ascending=True).head(10)





