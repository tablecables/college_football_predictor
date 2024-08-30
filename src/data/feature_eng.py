import pandas as pd
import numpy as np

def calculate_team_vs_team_win_rate(df):
    df = df.sort_values('start_date')
    
    # Create a new DataFrame 'check' from 'df'
    check = df[['matchup', 'team_id', 'win', 'start_date']].copy()
    
    # Create a unique identifier for each matchup
    check['matchup_id'] = check['matchup'].apply(lambda x: tuple(sorted(x)))
    
    # Calculate cumulative wins for each matchup
    check['cumulative_wins'] = check.groupby('matchup_id').cumcount()
    check.loc[check['win'] == 1, 'cumulative_wins'] += 1
    
    # Calculate total games played for each matchup
    check['total_games'] = check.groupby('matchup_id').cumcount() + 1
    
    # Calculate win rate
    check['win_rate'] = (check['cumulative_wins'] - check['win']) / (check['total_games'] - 1)
    check.loc[check['total_games'] == 1, 'win_rate'] = 0.5  # Default to 50% for first game
    
    # Ensure team_id matches the first team in the matchup
    check['is_team_a'] = check['team_id'] == check['matchup'].apply(lambda x: x[0])
    check.loc[~check['is_team_a'], 'win_rate'] = 1 - check.loc[~check['is_team_a'], 'win_rate']
    
    return check['win_rate']

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
    mvp_df = df[mvp_features + ['win']].copy()
    
    # Handle non-numeric columns
    mvp_df['is_home'] = mvp_df['is_home'].astype(int)
    mvp_df['neutral_site'] = mvp_df['neutral_site'].astype(int)
    mvp_df['conference_game'] = mvp_df['conference_game'].astype(int)
    
    # Add team vs team history feature
    mvp_df['team_vs_team_win_rate'] = calculate_team_vs_team_win_rate(mvp_df)
    
    # Add time-based feature
    mvp_df['games_played_in_season'] = mvp_df.groupby(['season', 'team_id']).cumcount() + 1
    
    return mvp_df
