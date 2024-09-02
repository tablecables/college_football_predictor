# exploratory data analysis
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.interpolate import interp1d, make_interp_spline
import os

POWER_5_CONFERENCES = {
    'SEC': 'SEC',
    'Big Ten': 'B1G',
    'ACC': 'ACC',
    'Big 12': 'B12',
    'Pac-12': 'PAC'
}

def show_unique_value_counts(df, column):
    """
    Display unique value counts for a given column in a dataframe,
    sorted from highest to lowest.
    
    Parameters:
    df (pandas.DataFrame): The dataframe to analyze
    column (str): The column name to count unique values
    """
    value_counts = df[column].value_counts()
    total_count = len(df)
    
    print(f"Unique value counts for {column}:")
    print("-" * 40)
    print(f"{'Value':<20} {'Count':<10} {'Percentage':<10}")
    print("-" * 40)
    
    for value, count in value_counts.items():
        percentage = (count / total_count) * 100
        print(f"{str(value):<20} {count:<10} {percentage:.2f}%")
    
    print("-" * 40)
    print(f"Total unique values: {len(value_counts)}")

def rank_teams_by_wins(df, years=10, curvature=0):
    # Filter data for the past 'years' and Power 5 conferences
    recent_years = df['season'].max() - years + 1
    df_filtered = df[(df['season'] >= recent_years) & (df['team_conference'].isin(POWER_5_CONFERENCES.keys()))]
    
    # Group by season and team_id, sum the wins
    wins_per_season = df_filtered.groupby(['season', 'team_id', 'team'])['win'].sum().reset_index()
    
    # Sort and rank teams for each season
    ranked_teams = wins_per_season.sort_values(['season', 'win'], ascending=[True, False])
    ranked_teams['rank'] = ranked_teams.groupby('season')['win'].rank(method='min', ascending=False)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Get teams that were #1 or tied for 1st in at least one year
    top_teams = set(ranked_teams[ranked_teams['rank'] == 1]['team_id'])
    
    # Plot curved lines for each team
    for team_id, team_data in ranked_teams.groupby('team_id'):
        seasons = team_data['season']
        wins = team_data['win']
        
        if len(seasons) > 1:
            if curvature > 0:
                # Create a smoother curve
                x_new = np.linspace(seasons.min(), seasons.max(), 200)
                spl = make_interp_spline(seasons, wins, k=min(3, len(seasons)-1))
                y_new = spl(x_new)
                
                # Mix between linear and curved
                f_linear = interp1d(seasons, wins, kind='linear')
                y_linear = f_linear(x_new)
                y_new = (1 - curvature) * y_linear + curvature * y_new
            else:
                # Keep it linear
                f_linear = interp1d(seasons, wins, kind='linear')
                x_new = np.linspace(seasons.min(), seasons.max(), 200)
                y_new = f_linear(x_new)
            
            if team_id in top_teams:
                ax.plot(x_new, y_new, label=team_data['team'].iloc[0], linewidth=2.5)
            else:
                ax.plot(x_new, y_new, color='grey', alpha=0.5, linewidth=1)
        else:
            if team_id in top_teams:
                ax.plot(seasons, wins, marker='o', label=team_data['team'].iloc[0], linewidth=2.5)
            else:
                ax.plot(seasons, wins, marker='o', color='grey', alpha=0.5, linewidth=1)
        
    # Add logos for #1 team(s) each season
    top_teams = ranked_teams[ranked_teams['rank'] == 1]
    for season, season_group in top_teams.groupby('season'):
        x = season
        base_y = season_group['win'].iloc[0]
        
        for i, (_, team) in enumerate(season_group.iterrows()):
            logo_path = f"../src/utils/logos/{team['team_id']}.png"
            if os.path.exists(logo_path):
                logo = plt.imread(logo_path)
                imagebox = OffsetImage(logo, zoom=1.00)
                # Distribute logos vertically, starting from the base_y and moving down
                y_offset = i * 0.8  # Adjust this value to change vertical spacing
                ab = AnnotationBbox(imagebox, (x, base_y - y_offset), frameon=False)
                ax.add_artist(ab)
    
    ax.set_xticks(range(recent_years, df['season'].max() + 1))
    ax.set_xlabel('Season')
    ax.set_ylabel('Wins')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Top Teams")
    plt.title(f"Power 5 Conference Team Performance over the Past {years} Years", fontsize=16)
    plt.tight_layout()
    plt.show()
    
    return ranked_teams

def correlation_analysis(df, target_col, top_n=15):
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Ensure target column is included
    if target_col not in numeric_df.columns:
        raise ValueError(f"Target column '{target_col}' is not numeric.")
    
    # Calculate correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Get correlations with target column
    target_correlations = corr_matrix[target_col].abs().sort_values(ascending=False)
    
    # Select top N features (excluding the target itself)
    top_features = target_correlations[1:top_n+1].index.tolist()
    
    # Create a subset of the correlation matrix
    subset_corr = corr_matrix.loc[top_features + [target_col], top_features + [target_col]]
    
    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(subset_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title(f'Correlation Heatmap: Top {top_n} Features vs {target_col}')
    plt.tight_layout()
    plt.show()
    
    return subset_corr