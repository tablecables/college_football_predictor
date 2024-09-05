# Data Transformations

from .warehouse import fetch_raw_data

def process_team_game_stats():
    df = fetch_raw_data('team_game_stats')
    if df is not None:
        # Expand the 'teams' column
        df = df.explode('teams')
        df = pd.concat([df.drop(['teams'], axis=1), 
                        df['teams'].apply(pd.Series)], axis=1)

        # Rename columns for clarity
        df = df.rename(columns={
            'school_id': 'team_id',
            'school': 'team_name',
            'conference': 'team_conference'
        })

        # Function to safely process stats
        def process_stats(stats):
            if isinstance(stats, list):
                return {item['category']: item['stat'] for item in stats if isinstance(item, dict) and 'category' in item and 'stat' in item}
            return {}

        # Explode the 'stats' column
        stats_df = df['stats'].apply(process_stats).apply(pd.Series)

        # Merge the exploded stats back into the main dataframe
        df = pd.concat([df.drop('stats', axis=1), stats_df], axis=1)

        # Convert numeric columns to appropriate types
        numeric_columns = df.columns.drop(['id', 'team_id', 'team_name', 'team_conference', 'home_away'])
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        return df
    return None