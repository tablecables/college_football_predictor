import pandas as pd
import numpy as np

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

def visualize_null_values(df):
    import matplotlib.pyplot as plt
    import seaborn as sns

    null_columns = df.columns[df.isnull().any()].tolist()
    null_percentages = df[null_columns].isnull().mean().sort_values(ascending=False) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 15))
    fig.patch.set_facecolor('#f0f0f0')

    sns.heatmap(df[null_columns].isnull(), cmap='YlGnBu', cbar=False, ax=ax1)
    ax1.set_title('Distribution of Null Values', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Columns', fontsize=12)
    ax1.set_ylabel('Rows', fontsize=12)
    ax1.set_xticks([])
    ax1.set_yticks([])

    null_percentages.plot(kind='barh', ax=ax2)
    ax2.set_title('Percentage of Null Values by Column', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Percentage of Null Values', fontsize=12)
    ax2.set_ylabel('Columns', fontsize=12)

    for i, v in enumerate(null_percentages):
        ax2.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=10)

    plt.tight_layout()
    fig.patch.set_edgecolor('black')
    fig.patch.set_linewidth(2)

    plt.show()

    print("Columns with null values:")
    for col in null_columns:
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / len(df)) * 100
        print(f"{col}: {null_count} null values ({null_percentage:.2f}%)")