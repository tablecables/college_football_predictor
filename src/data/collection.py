import cfbd
from cfbd.rest import ApiException
import os
from dotenv import load_dotenv
import pandas as pd
import random
import time
import sqlite3
from .warehouse import store_raw_data, get_last_update

# Define Power 5 conferences
POWER_5_CONFERENCES = {
    'SEC': 'SEC',
    'Big Ten': 'B1G',
    'ACC': 'ACC',
    'Big 12': 'B12',
    'Pac-12': 'PAC'
}

#! maybe remove
def convert_to_dataframe(games):
    return pd.DataFrame([game.to_dict() for game in games])

def load_api_key():
    load_dotenv()
    return os.getenv("API_KEY")

def configure_api(api_key):
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = api_key
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    return configuration

def initialize_games_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.GamesApi(cfbd.ApiClient(configuration))

def initialize_stats_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.StatsApi(cfbd.ApiClient(configuration))

def initialize_teams_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.TeamsApi(cfbd.ApiClient(configuration))

def fetch_games(start_year, end_year, games_api):
    last_season = get_last_update('games')
    all_games = []

    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for year in range(start_year, end_year + 1):
        year_games = []
        for conference in POWER_5_CONFERENCES.values():
            try:
                # Fetch regular season games
                regular_games = games_api.get_games(year=year, conference=conference, season_type='regular')
                if regular_games:
                    year_games.extend(regular_games)
                    print(f"Successfully fetched regular season games for {year}, conference: {conference}")
                else:
                    print(f"No regular season games found for {year}, conference: {conference}")
                
                # Fetch postseason games
                postseason_games = games_api.get_games(year=year, conference=conference, season_type='postseason')
                if postseason_games:
                    year_games.extend(postseason_games)
                    print(f"Successfully fetched postseason games for {year}, conference: {conference}")
                else:
                    print(f"No postseason games found for {year}, conference: {conference}")
                
            except ApiException as e:
                print(f"Exception when calling GamesApi->get_games for year {year}, conference {conference}: {e}\n")
        
        if year_games:
            df = convert_to_dataframe(year_games)
            if year == last_season:
                # Replace data for the last season
                store_raw_data(df, 'games', if_exists='replace')
                print(f"Replaced data for year {year}")
            else:
                # Append data for new years
                store_raw_data(df, 'games', if_exists='append')
                print(f"Appended data for year {year}")
            
            all_games.extend(year_games)

    if all_games:
        return convert_to_dataframe(all_games)
    return None

def fetch_team_game_stats(start_year, end_year):
    api_instance = initialize_games_api()
    
    all_team_stats = []
    for year in range(start_year, end_year + 1):
        for conference in POWER_5_CONFERENCES.values():
            try:
                team_stats = api_instance.get_team_game_stats(
                    year=year,
                    conference=conference,
                    season_type='regular'
                )
                all_team_stats.extend(team_stats)
                print(f"Successfully fetched team game stats for {year}, conference: {conference}")
            except ApiException as e:
                print(f"Exception when calling GamesApi->get_team_game_stats for year {year}, conference {conference}: {e}\n")
                print(f"Response body: {e.body}\n")
    
    if not all_team_stats:
        return None

    # Convert to DataFrame
    team_stats_df = convert_to_dataframe(all_team_stats)
    
    # Expand the 'teams' column
    team_stats_df = team_stats_df.explode('teams')
    team_stats_df = pd.concat([team_stats_df.drop(['teams'], axis=1), 
                               team_stats_df['teams'].apply(pd.Series)], axis=1)

    # Rename columns for clarity
    team_stats_df = team_stats_df.rename(columns={
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
    stats_df = team_stats_df['stats'].apply(process_stats).apply(pd.Series)

    # Merge the exploded stats back into the main dataframe
    team_stats_df = pd.concat([team_stats_df.drop('stats', axis=1), stats_df], axis=1)

    # Convert numeric columns to appropriate types
    numeric_columns = team_stats_df.columns.drop(['id', 'team_id', 'team_name', 'team_conference', 'home_away'])
    team_stats_df[numeric_columns] = team_stats_df[numeric_columns].apply(pd.to_numeric, errors='ignore')

    return team_stats_df

def fetch_advanced_team_game_stats(start_year, end_year, df, max_teams=None):
    api_instance = initialize_stats_api()
    
    all_stats = []
    start_time = time.time()
    
    # Get unique team-year combinations from df
    team_years = df[['season', 'home_team']].rename(columns={'home_team': 'team'}).drop_duplicates()
    team_years = pd.concat([team_years, df[['season', 'away_team']].rename(columns={'away_team': 'team'})]).drop_duplicates()
    
    # Filter for the specified year range
    team_years = team_years[(team_years['season'] >= start_year) & (team_years['season'] <= end_year)]
    
    # If max_teams is specified, randomly sample teams
    if max_teams:
        unique_teams = team_years['team'].unique()
        sampled_teams = random.sample(list(unique_teams), min(max_teams, len(unique_teams)))
        team_years = team_years[team_years['team'].isin(sampled_teams)]
    
    total_teams = len(team_years)
    for index, (_, row) in enumerate(team_years.iterrows(), 1):
        year = row['season']
        team = row['team']
        try:
            team_stats = api_instance.get_advanced_team_game_stats(
                year=year,
                team=team,
                exclude_garbage_time=True,
                season_type='regular'
            )
            all_stats.extend(team_stats)
            if index % 10 == 0 or index == total_teams:
                print(f"Progress: {index}/{total_teams} teams processed")
        except ApiException as e:
            print(f"Error fetching data for {team} in {year}: {e}")
        
        time.sleep(0.5)  # Add a small delay to avoid hitting rate limits
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Convert to DataFrame
    df_stats = convert_to_dataframe(all_stats)
    
    return df_stats, execution_time

def fetch_team_talent(start_year, end_year):
    api_instance = initialize_teams_api()
    
    all_talent = []
    for year in range(start_year, end_year + 1):
        try:
            talent = api_instance.get_talent(year=year)
            all_talent.extend(talent)
            print(f"Successfully fetched team talent data for {year}")
        except ApiException as e:
            print(f"Exception when calling TeamsApi->get_talent for year {year}: {e}\n")
    
    return convert_to_dataframe(all_talent) if all_talent else None