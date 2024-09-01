import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def create_team_centric_df(games_df):
    # Filter for completed games
    completed_games = games_df[games_df['completed'] == True]
    
    # Define common columns to keep
    common_cols = ['id', 'season', 'week', 'season_type', 'start_date', 'neutral_site', 
                   'conference_game', 'attendance', 'venue_id', 'venue', 
                   'excitement_index', 'highlights', 'notes']
    
    home_df = completed_games.rename(columns={
        'home_id': 'team_id',
        'home_team': 'team',
        'home_conference': 'team_conference',
        'home_division': 'team_division',
        'home_points': 'team_points',
        'away_id': 'opponent_id',
        'away_team': 'opponent',
        'away_conference': 'opponent_conference',
        'away_division': 'opponent_division',
        'away_points': 'opponent_points'
    })
    home_df['is_home'] = True

    away_df = completed_games.rename(columns={
        'away_id': 'team_id',
        'away_team': 'team',
        'away_conference': 'team_conference',
        'away_division': 'team_division',
        'away_points': 'team_points',
        'home_id': 'opponent_id',
        'home_team': 'opponent',
        'home_conference': 'opponent_conference',
        'home_division': 'opponent_division',
        'home_points': 'opponent_points'
    })
    away_df['is_home'] = False

    # Select columns to keep
    columns_to_keep = common_cols + ['team_id', 'team', 'team_division', 
                                     'team_points', 'opponent_id', 'opponent', 
                                     'opponent_conference', 'opponent_division', 
                                     'opponent_points', 'is_home']

    team_centric_df = pd.concat([home_df[columns_to_keep], away_df[columns_to_keep]], ignore_index=True)
    return team_centric_df

def merge_and_clean_dataframes(games_df, team_stats_df, advanced_stats_df, team_talent_df):
    # Create team-centric dataframe
    team_centric_df = create_team_centric_df(games_df)

    # Merge with team_stats_df
    merged_df = pd.merge(team_centric_df, team_stats_df, on=['id', 'team_id'], how='left', suffixes=('', '_stats'))

    # Remove duplicate columns
    columns_to_drop = [col for col in merged_df.columns if col.endswith('_stats')]
    merged_df = merged_df.drop(columns=columns_to_drop)

    # Rename 'points' to 'team_points_stats' to avoid confusion
    merged_df = merged_df.rename(columns={'points': 'team_points_stats'})

    # Add point difference and result columns
    merged_df['point_difference'] = merged_df['team_points'] - merged_df['opponent_points']
    merged_df['result'] = np.select(
        [merged_df['point_difference'] > 0, merged_df['point_difference'] < 0, merged_df['point_difference'] == 0],
        ['win', 'loss', 'tie'],
        default='unknown'
    )

    # Normalize advanced stats
    offense_cols = pd.json_normalize(advanced_stats_df['offense']).add_prefix('offense_')
    defense_cols = pd.json_normalize(advanced_stats_df['defense']).add_prefix('defense_')
    # Combine the expanded dataframe
    advanced_stats_final = pd.concat([advanced_stats_df[['game_id', 'week', 'team']], 
                                      offense_cols, defense_cols], axis=1)

    # Merge with merged_df
    merged_df_final = merged_df.merge(advanced_stats_final, 
                                      left_on=['id', 'week', 'team'], 
                                      right_on=['game_id', 'week', 'team'], 
                                      how='left')

    # Drop the redundant game_id column
    merged_df_final = merged_df_final.drop('game_id', axis=1)

    # Merge with advanced_stats_df
    merged_df_final = merged_df.merge(advanced_stats_final, 
                                      left_on=['id', 'week', 'team'], 
                                      right_on=['game_id', 'week', 'team'], 
                                      how='left')

    # Drop the redundant game_id column
    merged_df_final = merged_df_final.drop('game_id', axis=1)

    # Merge team_talent_df with merged_df_final
    merged_df_final = merged_df_final.merge(
        team_talent_df.rename(columns={'year': 'season', 'school': 'team', 'talent': 'team_talent'}),
        on=['season', 'team'],
        how='left'
    )

    merged_df_final = merged_df_final.merge(
        team_talent_df.rename(columns={'year': 'season', 'school': 'opponent', 'talent': 'opponent_talent'}),
        on=['season', 'opponent'],
        how='left'
    )

    return merged_df_final

def clean_dataframe(df_og):
    df = df_og.copy()
    # Drop rows where season is 2024
    df = df[df['season'] != 2024]
    
    # Columns to drop
    columns_to_drop = [
        'highlights', 'notes'
    ]
    df = df.drop(columns=columns_to_drop)
    
    # Set totalFumbles as sum of fumblesLost and fumblesRecovered
    df['totalFumbles'] = df['fumblesLost'].fillna(0) + df['fumblesRecovered'].fillna(0)

    # Handle advanced stats columns
    advanced_stats_columns = [col for col in df.columns if col.startswith(('offense_', 'defense_'))]
    
    # Drop rows where all advanced stats columns are null
    df = df.dropna(subset=advanced_stats_columns, how='all')
    
    # Columns to fill with 0
    columns_to_fill_zero = [
        'puntReturnYards', 'puntReturnTDs', 'puntReturns',
        'kickingPoints', 'interceptionYards', 'interceptionTDs',
        'passesIntercepted', 'passingTDs', 'rushingTDs'
    ]
    df[columns_to_fill_zero] = df[columns_to_fill_zero].fillna(0)
    
    # Create placeholder values for missing venue information
    null_venue_id = -1  # or 0, depending on your preference
    null_venue_name = "Unknown Venue"

    # Fill null values
    df['venue_id'] = df['venue_id'].fillna(null_venue_id)
    df['venue'] = df['venue'].fillna(null_venue_name)

     # Helper function to safely calculate median
    def safe_median(x):
        return x.median() if len(x) > 0 and not x.isna().all() else np.nan

    # Handle attendance
    if 'venue_id' in df.columns and 'season' in df.columns:
        # Create a mask for non-2020 seasons with zero attendance
        mask = (df['season'] != 2020) & (df['attendance'] == 0)
        
        # Fill with median from that year for that venue_id
        df.loc[mask, 'attendance'] = df[mask].groupby(['season', 'venue_id'])['attendance'].transform(safe_median)
        
        # If there are still zero values, fill with median for that team and season
        df.loc[mask, 'attendance'] = df[mask].groupby(['season', 'team'])['attendance'].transform(safe_median)
    
        # If there are still zero values in attendance, fill with overall median for that season
        df.loc[mask, 'attendance'] = df[mask].groupby('season')['attendance'].transform(safe_median)
    
    # Handle null values in attendance
    mask_null = df['attendance'].isnull()
    df.loc[mask_null, 'attendance'] = df[mask_null].groupby(['season', 'venue_id'])['attendance'].transform(safe_median)
    df.loc[mask_null, 'attendance'] = df[mask_null].groupby(['season', 'team'])['attendance'].transform(safe_median)
    df.loc[mask_null, 'attendance'] = df[mask_null].groupby('season')['attendance'].transform(safe_median)
    
    # Handle other columns and open_field_yards columns
    columns_to_handle = ['offense_open_field_yards', 'offense_open_field_yards_total',
                         'defense_open_field_yards', 'defense_open_field_yards_total']
    
    for col in columns_to_handle:
        # Fill with median for that team and season
        df[col] = df.groupby(['team', 'season'])[col].transform(safe_median)
        
        # If there are still null values, fill with overall median for that season
        df[col] = df.groupby('season')[col].transform(safe_median)
    
    # Handle columns with very few null values, explosiveness columns, and PPA columns
    columns_to_fill = [
        'offense_second_level_yards', 'offense_second_level_yards_total',
        'defense_second_level_yards', 'defense_second_level_yards_total',
        'offense_rushing_plays.explosiveness', 'offense_standard_downs.explosiveness',
        'defense_rushing_plays.explosiveness', 'defense_standard_downs.explosiveness',
        'offense_passing_downs.explosiveness', 'offense_passing_plays.explosiveness',
        'defense_passing_downs.explosiveness', 'defense_passing_plays.explosiveness',
        'offense_passing_plays.ppa', 'offense_passing_plays.total_ppa',
        'defense_passing_plays.ppa', 'defense_passing_plays.total_ppa',
        'offense_explosiveness', 'defense_explosiveness'
    ]
    
    for col in columns_to_fill:
        df[col] = df.groupby(['team', 'season'])[col].transform(safe_median)
        # If there are still null values, fill with overall median for that season
        df[col] = df.groupby('season')[col].transform(lambda x: x.fillna(safe_median(x)))
        # If there are still null values, fill with dataset median
        df[col] = df[col].fillna(df[col].median())
    
    # Handle possessionTime separately
    def convert_to_seconds(time_str):
        if pd.isna(time_str):
            return np.nan
        try:
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
        except:
            return np.nan

    df['possessionTime'] = df['possessionTime'].apply(convert_to_seconds)
    
    # Now apply the same filling logic as before
    df['possessionTime'] = df.groupby(['team', 'season'])['possessionTime'].transform(safe_median)
    df['possessionTime'] = df.groupby('season')['possessionTime'].transform(lambda x: x.fillna(safe_median(x)))
    df['possessionTime'] = df['possessionTime'].fillna(df['possessionTime'].median())
    
    # Convert back to MM:SS format
    df['possessionTime'] = df['possessionTime'].apply(lambda x: f"{int(x // 60):02d}:{int(x % 60):02d}" if not pd.isna(x) else np.nan)
    
    # Drop rows where both team columns or both opponent columns are null
    team_columns = ['team_conference', 'team_division']
    opponent_columns = ['opponent_conference', 'opponent_division']
    
    # Drop rows where both team columns are null
    df = df.dropna(subset=team_columns, how='all')
    
    # Drop rows where both opponent columns are null
    df = df.dropna(subset=opponent_columns, how='all')
    
    return df

def generate_and_save_team_pairs(cleaned_df, project_root):
    # Create a DataFrame showing individual team_id team pairs
    team_pairs_df = cleaned_df[['team_id', 'team']].drop_duplicates().reset_index(drop=True)

    # Convert the DataFrame to a list of tuples
    team_pairs_list = list(team_pairs_df.itertuples(index=False, name=None))

    # Format the team pairs list with line breaks
    formatted_pairs = ',\n    '.join(repr(pair) for pair in team_pairs_list)

    # Generate the Python code as a string
    python_code = f"""
# This file is auto-generated. Do not edit manually.

TEAM_PAIRS = [
    {formatted_pairs}
]

def get_team_pairs():
    return TEAM_PAIRS

def is_valid_pair(team1, team2):
    return (team1, team2) in TEAM_PAIRS or (team2, team1) in TEAM_PAIRS
"""

    # Define the path for the utils directory and the team_pairs.py file
    utils_dir = os.path.join(project_root, 'src', 'utils')
    team_pairs_path = os.path.join(utils_dir, 'team_pairs.py')

    # Create the utils directory if it doesn't exist
    os.makedirs(utils_dir, exist_ok=True)

    # Write the Python code to the file
    with open(team_pairs_path, 'w') as f:
        f.write(python_code)

    return team_pairs_path

def deduplicate_dataframes(*dataframes, df_names=None):
    """
    Deduplicate multiple dataframes efficiently, excluding advanced_stats_df.
    
    Args:
    *dataframes: Variable number of pandas DataFrames
    df_names: List of names for the dataframes (optional)
    
    Returns:
    list: List of deduplicated DataFrames
    int: Total number of rows dropped across all dataframes
    """
    if df_names is None:
        df_names = [f"DataFrame_{i}" for i in range(len(dataframes))]
    
    total_rows_dropped = 0
    deduplicated_dfs = []

    for df, name in zip(dataframes, df_names):
        if name == "advanced_stats_df":
            print(f"Skipping deduplication for {name}")
            deduplicated_dfs.append(df)
            continue

        initial_rows = len(df)
        
        # Convert problematic columns to strings
        for col in df.select_dtypes(include=[object]).columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str)
        
        # Drop duplicates
        df = df.drop_duplicates()
        
        rows_dropped = initial_rows - len(df)
        total_rows_dropped += rows_dropped
        
        print(f"{name}: Dropped {rows_dropped} duplicate rows")
        deduplicated_dfs.append(df)
    
    print(f"\nTotal duplicate rows dropped across all dataframes: {total_rows_dropped}")
    
    return deduplicated_dfs, total_rows_dropped