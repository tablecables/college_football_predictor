# feature engineering

import pandas as pd
import numpy as np
from .constants.EXISTING_FEATURES import EXISTING_FEATURES
from .constants.ENGINEERED_FEATURES import ENGINEERED_FEATURES

# combine all features

ALL_FEATURES = EXISTING_FEATURES + ENGINEERED_FEATURES

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
    def weighted_avg(group):
        values = group[stat].values
        size = len(values)
        if size <= 1:
            return pd.Series([np.nan] * size, index=group.index)
        
        weights = np.arange(1, size)
        cumsum_vals = np.cumsum(values[:-1] * weights)
        cumsum_weights = np.cumsum(weights)
        
        result = cumsum_vals / cumsum_weights
        return pd.Series(np.concatenate(([np.nan], result)), index=group.index)

    # Sort the data by team_id and start_date
    data = data.sort_values(['team_id', 'start_date'])
    
    # Calculate the weighted average
    result = data.groupby('team_id', group_keys=False).apply(weighted_avg)
    
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

def get_engineered_feature_functions():
    functions = {}
    for feature in ENGINEERED_FEATURES:
        if 'variants' in feature:
            for variant in feature['variants']:
                func_name = f"{feature['base_name']}_{variant['suffix']}"
                params = variant.get('params', {})
                functions[func_name] = lambda df, stat=feature['base_name'], func=variant['function'], params=params: globals()[func](df, stat, **params) if stat in df.columns else pd.Series(np.nan, index=df.index)
        else:
            func_name = feature['name']
            params = feature.get('params', {})
            functions[func_name] = lambda df, func=feature['function'], params=params: globals()[func](df, **params)
    return functions

def get_feature_names(feature_type=None):
    if feature_type == "engineered":
        engineered_names = []
        for feature in ENGINEERED_FEATURES:
            if 'variants' in feature:
                engineered_names.extend([f"{feature['base_name']}_{variant['suffix']}" 
                                         for variant in feature['variants']])
            else:
                engineered_names.append(feature['name'])
        return engineered_names
    elif feature_type:
        return [f["name"] for f in ALL_FEATURES if f["type"] == feature_type]
    return [f["name"] for f in ALL_FEATURES if f["type"] == "existing"] + get_feature_names("engineered")

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all engineered features to the dataframe."""
    engineered_funcs = get_engineered_feature_functions()
    
    # Calculate all engineered features at once
    new_features = {}
    for feature_name, func in engineered_funcs.items():
        if feature_name not in df.columns:  # Only add if not already present
            try:
                new_feature = func(df)
                new_features[feature_name] = new_feature
            except KeyError as e:
                print(f"Warning: Could not calculate {feature_name}. Missing column: {str(e)}")
            except Exception as e:
                print(f"Error calculating {feature_name}: {str(e)}")
    
    # Create a new DataFrame with engineered features and concatenate with original
    engineered_df = pd.DataFrame(new_features, index=df.index)
    return pd.concat([df, engineered_df], axis=1)

def select_features(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Select specified features from the dataframe."""
    if selected_features is None:
        selected_features = get_feature_names()
    
    # Only select features that exist in the dataframe
    existing_features = [f for f in selected_features if f in df.columns]
    return df[existing_features]

def preprocess_data(df: pd.DataFrame, selected_features: list = None) -> pd.DataFrame:
    """Main function to preprocess data: engineer features and select them."""
    df = engineer_features(df)  # Engineer features first
    df = select_features(df, selected_features)  # Then select features
    return df