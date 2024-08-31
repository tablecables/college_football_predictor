import pandas as pd
import numpy as np

def calculate_team_vs_team_win_rate(df):
    # Create a new DataFrame 'check' from 'df'
    check = df[['matchup', 'team_id', 'opponent_id', 'win']].copy()
    
    # Convert matchup from numpy array to tuple
    check['matchup'] = check['matchup'].apply(tuple)
    
    # Extract team IDs from the matchup tuple
    check['a'] = check['matchup'].apply(lambda x: x[0])
    check['b'] = check['matchup'].apply(lambda x: x[1])
    
    # Initialize columns for wins
    check['a_wins'] = 0
    check['b_wins'] = 0
    
    # Update 'a_wins' and 'b_wins'
    check.loc[((check['team_id'] == check['a']) & (check['win'] == 1)) | 
              ((check['opponent_id'] == check['a']) & (check['win'] == 0)), 'a_wins'] = 1
    check.loc[((check['team_id'] == check['b']) & (check['win'] == 1)) | 
              ((check['opponent_id'] == check['b']) & (check['win'] == 0)), 'b_wins'] = 1
    
    # Group by matchup and sum the wins for each team
    grouped = check.groupby('matchup').agg({'a_wins': 'sum', 'b_wins': 'sum'}).reset_index()
    
    # Calculate win_rate
    grouped['win_rate'] = grouped['a_wins'] / (grouped['a_wins'] + grouped['b_wins'])
    
    # Merge the win_rate back to the original dataframe
    result = pd.merge(check, grouped[['matchup', 'win_rate']], on='matchup', how='left')
    
    # Adjust win_rate for team_b
    result.loc[result['team_id'] == result['b'], 'win_rate'] = 1 - result['win_rate']
    
    return result['win_rate']

def calculate_all_time_win_rate(df):
    df = df.sort_values('start_date')
    df['cumulative_wins'] = df.groupby('team_id')['win'].cumsum()
    df['games_played'] = df.groupby('team_id').cumcount() + 1
    df['all_time_win_rate'] = df['cumulative_wins'] / df['games_played']
    return df['all_time_win_rate'].shift(1).fillna(0.5)

def calculate_season_win_rate(df):
    df = df.sort_values(['season', 'start_date'])
    df['cumulative_season_wins'] = df.groupby(['season', 'team_id'])['win'].cumsum()
    df['season_games_played'] = df.groupby(['season', 'team_id']).cumcount() + 1
    df['season_win_rate'] = df['cumulative_season_wins'] / df['season_games_played']
    return df['season_win_rate'].shift(1).fillna(0.5)

def select_mvp_features(df):
    mvp_features = [
        # Game identifiers
        'season', 'week', 'team_id', 'opponent_id', 'matchup',
        
        # Game context
        'is_home', 'neutral_site', 'conference_game',
        
        # Team performance
        'team_points', 'opponent_points',
        'totalYards', 'rushingYards', 'netPassingYards',
        'turnovers', 'firstDowns',
        
        # Advanced metrics
        'offense_success_rate', 'defense_success_rate',
        'offense_explosiveness', 'defense_explosiveness',
        'offense_ppa', 'defense_ppa',
        
        # Team quality
        'team_talent', 'opponent_talent'
    ]
    
    # Select MVP features
    mvp_df = df[mvp_features + ['win', 'start_date']].copy()
    
    # Handle non-numeric columns
    mvp_df['is_home'] = mvp_df['is_home'].astype(int)
    mvp_df['neutral_site'] = mvp_df['neutral_site'].astype(int)
    mvp_df['conference_game'] = mvp_df['conference_game'].astype(int)
    
    # Add team vs team history feature
    mvp_df['team_vs_team_win_rate'] = calculate_team_vs_team_win_rate(mvp_df)
    
    # Add time-based feature
    mvp_df['games_played_in_season'] = mvp_df.groupby(['season', 'team_id']).cumcount() + 1
    
    # Add all-time and season win rates
    mvp_df['all_time_win_rate'] = calculate_all_time_win_rate(mvp_df)
    mvp_df['season_win_rate'] = calculate_season_win_rate(mvp_df)
    
    # Drop the 'start_date' column as it was only used for calculations
    mvp_df = mvp_df.drop('start_date', axis=1)
    
    return mvp_df
