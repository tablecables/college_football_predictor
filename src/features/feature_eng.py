# feature engineering

import pandas as pd
import numpy as np

def calculate_rolling_average(data, stat, n):
    # Ensure data is sorted by game date and team_id
    data = data.sort_values(by=['team_id', 'start_date'])
    
    return (
        data.groupby('team_id')[stat]
        .rolling(window=n, min_periods=n)
        .mean()
        .shift()
        .reset_index(level=0, drop=True)
    )

def calculate_total_points_last_n(data, stat, n):
    # Sort the dataframe by team_id and start_date
    df = data.sort_values(['team_id', 'start_date'])
    
    # Define a function to calculate the rolling sum for each group
    def rolling_sum(group):
        return group.shift().rolling(window=n, min_periods=n).sum()
    
    # Apply the rolling sum function to each team's group
    result = df.groupby('team_id')[stat].transform(rolling_sum)
    
    return result

def calculate_weighted_average(data, stat):
    # Ensure data is sorted by game date and team_id
    data = data.sort_values(by=['team_id', 'start_date'])
    
    def weighted_avg(group):
        values = group.values.flatten()  # Flatten the array to ensure 1D
        size = len(values)
        
        weights = np.arange(1, size + 1)
        cumsum_vals = np.cumsum(values * weights[::-1])
        cumsum_weights = np.cumsum(weights[::-1])
        
        result = cumsum_vals / cumsum_weights
        return pd.Series(result[::-1], index=group.index)

    # Calculate the weighted average
    result = (
        data.groupby('team_id')[stat]
        .apply(weighted_avg)
        .reset_index(level=0, drop=True)
        .shift()
    )
    
    return result
    
def calculate_win_rate_last_n(data, n):
    # Sort the dataframe by team_id and start_date
    df = data.sort_values(['team_id', 'start_date'])
    
    # Define a function to calculate the rolling win rate for each group
    def rolling_win_rate(group):
        # Shift to exclude current game, then calculate rolling sum of wins and count of games
        wins = group.shift().rolling(window=n, min_periods=n).sum()
        games = group.shift().rolling(window=n, min_periods=n).count()
        
        # Calculate win rate
        win_rate = wins / games
        
        # Replace win rate with NaN where we don't have enough games
        win_rate = win_rate.where(games == n, np.nan)
        
        return win_rate
    
    # Apply the rolling win rate function to each team's group
    result = df.groupby('team_id')['win'].transform(rolling_win_rate)
    
    return result

def calculate_season_average_corrected(data, stat):
    # Sort the data by team_id, season, and start_date
    data = data.sort_values(['team_id', 'season', 'start_date'], ascending=True)
    
    # Calculate the cumulative sum and count of the stat
    cumsum = data.groupby(['team_id', 'season'])[stat].cumsum()
    cumcount = data.groupby(['team_id', 'season']).cumcount() + 1
    
    # Shift both cumsum and cumcount to exclude the current game
    cumsum_shifted = cumsum.shift()
    cumcount_shifted = cumcount.shift()
    
    # Calculate the season-to-date average, excluding the current game
    season_avg = cumsum_shifted / cumcount_shifted
    
    # Identify the first game of each team-season combination
    first_game = data.groupby(['team_id', 'season']).transform('first')
    
    # Set NaN for the first game of each team-season combination
    season_avg[first_game[stat] == data[stat]] = np.nan
    
    return season_avg

def calculate_season_win_rate(data):
    print("Calculating season win rate")  # Debug print
    
    # Ensure data is sorted by game date and team_id
    data = data.sort_values(by=['team_id', 'season', 'start_date'])
    
    # Calculate win rate for the season
    win_rate = (
        data.groupby(['team_id', 'season'])['win']
        .expanding()
        .mean()
        .reset_index(level=[0, 1], drop=True)
        .shift()
    )
    
    print(f"Season win rate calculation complete. Shape: {win_rate.shape}")  # Debug print
    
    return win_rate

def calculate_season_point_differential(data):
    return data.groupby(['team_id', 'season'])['point_difference'].transform(lambda x: x.shift().expanding().mean())

def calculate_cumulative_season_point_differential(data):
    return data.groupby(['team_id', 'season'])['point_difference'].transform(lambda x: x.shift().cumsum())

