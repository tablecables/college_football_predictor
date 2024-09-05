import cfbd
from cfbd.rest import ApiException
import os
from dotenv import load_dotenv
import pandas as pd
import random
import time
from .warehouse import (
    store_raw_data,
    get_last_update,
    fetch_raw_data,
    store_calendar_data,
    fetch_calendar_data
)

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
            games_data = [game.to_dict() for game in year_games]
            if year == last_season:
                # Replace data for the last season
                store_raw_data(games_data, 'games', if_exists='replace')
                print(f"Replaced data for year {year}")
            else:
                # Append data for new years
                store_raw_data(games_data, 'games', if_exists='append')
                print(f"Appended data for year {year}")

    print("Finished fetching games data")

def fetch_team_game_stats(start_year, end_year):
    api_instance = initialize_games_api()
    last_season = get_last_update('team_game_stats')

    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for year in range(start_year, end_year + 1):
        year_stats = []
        for conference in POWER_5_CONFERENCES.values():
            try:
                team_stats = api_instance.get_team_game_stats(
                    year=year,
                    conference=conference,
                    season_type='regular'
                )
                year_stats.extend(team_stats)
                print(f"Successfully fetched team game stats for {year}, conference: {conference}")
            except ApiException as e:
                print(f"Exception when calling GamesApi->get_team_game_stats for year {year}, conference {conference}: {e}\n")
                print(f"Response body: {e.body}\n")
        
        if year_stats:
            stats_data = [stat.to_dict() for stat in year_stats]
            if year == last_season:
                # Replace data for the last season
                store_raw_data(stats_data, 'team_game_stats', if_exists='replace')
                print(f"Replaced team game stats data for year {year}")
            else:
                # Append data for new years
                store_raw_data(stats_data, 'team_game_stats', if_exists='append')
                print(f"Appended team game stats data for year {year}")

    print("Finished fetching team game stats data")

def get_games_df():
    raw_data = fetch_raw_data('games')
    return pd.DataFrame(raw_data)

def get_team_game_stats_df():
    raw_data = fetch_raw_data('team_game_stats')
    df = pd.DataFrame(raw_data)
    return process_team_game_stats(df)

def process_team_game_stats(df):
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
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='ignore')

    return df

def fetch_advanced_team_game_stats(start_year, end_year, stats_api):
    last_season = get_last_update('advanced_team_game_stats')
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for year in range(start_year, end_year + 1):
        year_stats = []
        for season_type in ['regular', 'postseason']:
            try:
                advanced_stats = stats_api.get_advanced_team_game_stats(
                    year=year,
                    exclude_garbage_time=True,
                    season_type=season_type
                )
                year_stats.extend([stat.to_dict() for stat in advanced_stats])
                print(f"Successfully fetched advanced team game stats for {year} {season_type} season")
            except ApiException as e:
                print(f"Exception when calling StatsApi->get_advanced_team_game_stats for year {year} {season_type} season: {e}\n")
                print(f"Response body: {e.body}\n")
            
            time.sleep(1)  # Add a delay to avoid hitting rate limits
        
        if year_stats:
            if year == last_season:
                # Replace data for the last season
                store_raw_data(year_stats, 'advanced_team_game_stats', if_exists='replace')
                print(f"Replaced advanced team game stats data for year {year}")
            else:
                # Append data for new years
                store_raw_data(year_stats, 'advanced_team_game_stats', if_exists='append')
                print(f"Appended advanced team game stats data for year {year}")

    print("Finished fetching advanced team game stats data")

def fetch_team_talent(start_year, end_year, api_instance):
    last_season = get_last_update('team_talent')
    
    # Ensure start_year is at least 2015
    start_year = max(2015, start_year)
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = max(2015, last_season)
    
    for year in range(start_year, end_year + 1):
        try:
            talent = api_instance.get_talent(year=year)
            talent_data = [item.to_dict() for item in talent]
            
            if year == last_season:
                # Replace data for the last season
                store_raw_data(talent_data, 'team_talent', if_exists='replace')
                print(f"Replaced team talent data for year {year}")
            else:
                # Append data for new years
                store_raw_data(talent_data, 'team_talent', if_exists='append')
                print(f"Appended team talent data for year {year}")
            
            print(f"Successfully fetched team talent data for {year}")
        except ApiException as e:
            print(f"Exception when calling TeamsApi->get_talent for year {year}: {e}\n")
    
    print("Finished fetching team talent data")

def fetch_calendar(year, games_api):
    try:
        calendar = games_api.get_calendar(year)
        calendar_data = [week.to_dict() for week in calendar]
        store_calendar_data(calendar_data, year)
        print(f"Successfully fetched and stored calendar data for {year}")
        return calendar_data
    except ApiException as e:
        print(f"Exception when calling GamesApi->get_calendar for year {year}: {e}\n")
        return None

def get_calendar(year, games_api):
    # First, try to fetch from the database
    calendar_data = fetch_calendar_data(year)
    
    # If not found in the database, fetch from the API and store
    if calendar_data is None:
        calendar_data = fetch_calendar(year, games_api)
    
    return calendar_data