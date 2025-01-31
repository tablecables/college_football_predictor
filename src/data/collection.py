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
    fetch_calendar_data,
    store_team_game_stats,
    store_advanced_team_game_stats
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

def initialize_ratings_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.RatingsApi(cfbd.ApiClient(configuration))

def initialize_metrics_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.MetricsApi(cfbd.ApiClient(configuration))

def initialize_recruiting_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.RecruitingApi(cfbd.ApiClient(configuration))

def initialize_betting_api():
    api_key = load_api_key()
    configuration = configure_api(api_key)
    return cfbd.BettingApi(cfbd.ApiClient(configuration))

def fetch_games(start_year, end_year, games_api, use_last_season=True):
    last_season = get_last_update('games') if use_last_season else None
    
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
            # Update or append data for this specific year
            store_raw_data(games_data, 'games', year=year)
            print(f"Updated/Appended data for year {year}")

    print("Finished fetching games data")

def fetch_team_game_stats(start_year, end_year, use_last_season=True):
    api_instance = initialize_games_api()
    last_season = get_last_update('games') if use_last_season else None
    
    # Set minimum year to 2004
    MIN_YEAR = 2004
    start_year = max(start_year, MIN_YEAR)
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for year in range(start_year, end_year + 1):
        year_stats = []
        for conference in POWER_5_CONFERENCES.values():
            for season_type in ['regular', 'postseason']:
                try:
                    team_stats = api_instance.get_team_game_stats(
                        year=year,
                        conference=conference,
                        season_type=season_type
                    )
                    year_stats.extend(team_stats)
                    print(f"Successfully fetched team game stats for {year}, conference: {conference}, season type: {season_type}")
                except ApiException as e:
                    print(f"Exception when calling GamesApi->get_team_game_stats for year {year}, conference {conference}, season type {season_type}: {e}\n")
                    print(f"Response body: {e.body}\n")
                
                time.sleep(1)  # Add a delay to avoid hitting rate limits
        
        if year_stats:
            stats_data = [stat.to_dict() for stat in year_stats]
            store_team_game_stats(stats_data, 'team_game_stats')
            print(f"Updated/Appended team game stats data for year {year}")
    
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

def fetch_advanced_team_game_stats(start_year, end_year, stats_api, use_last_season=True):
    last_season = get_last_update('games') if use_last_season else None
    
    # Set minimum year to 2004
    MIN_YEAR = 2004
    start_year = max(start_year, MIN_YEAR)
    
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
            store_advanced_team_game_stats(year_stats, 'advanced_team_game_stats')
            print(f"Updated/Appended advanced team game stats data for year {year}")
    
    print("Finished fetching advanced team game stats data")


def fetch_team_talent(start_year, end_year, api_instance, use_last_season=True):
    last_season = get_last_update('games') if use_last_season else None
    
    # Ensure start_year is at least 2015
    start_year = max(2015, start_year)
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = max(2015, last_season)
    
    for year in range(start_year, end_year + 1):
        try:
            talent = api_instance.get_talent(year=year)
            talent_data = [item.to_dict() for item in talent]
            
            # Include 'year' in each data item
            for item in talent_data:
                item['year'] = year
            
            if last_season is not None and year == last_season:
                # Replace data for the last season
                store_raw_data(talent_data, 'team_talent', if_exists='replace', year=year)
                print(f"Replaced team talent data for year {year}")
            else:
                # Append data for new years
                store_raw_data(talent_data, 'team_talent', if_exists='append', year=year)
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

def get_calendar(start_year, end_year, games_api):
    all_calendar_data = []
    for year in range(start_year, end_year + 1):
        # First, try to fetch from the database
        calendar_data = fetch_calendar_data(year)
        
        # If not found in the database, fetch from the API and store
        if calendar_data is None:
            calendar_data = fetch_calendar(year, games_api)
        
        if calendar_data:
            all_calendar_data.extend(calendar_data)
    
    return all_calendar_data

def fetch_ratings(start_year, end_year, ratings_api, rating_type):
    for year in range(start_year, end_year + 1):
        all_data = []
        try:
            if rating_type == 'elo':
                ratings = ratings_api.get_elo_ratings(year=year)
            elif rating_type == 'fpi':
                ratings = ratings_api.get_fpi_ratings(year=year)
            elif rating_type == 'sp':
                ratings = ratings_api.get_sp_ratings(year=year)
            elif rating_type == 'srs':
                ratings = ratings_api.get_srs_ratings(year=year)
            else:
                raise ValueError(f"Unknown rating type: {rating_type}")
            
            data = [rating.to_dict() for rating in ratings]
            all_data.extend(data)
            print(f"Successfully fetched {rating_type.upper()} ratings for {year}")
        except ApiException as e:
            print(f"Exception when calling RatingsApi->get_{rating_type}_ratings for year {year}: {e}\n")
        
        time.sleep(1)  # Add a delay to avoid hitting rate limits
        
        if all_data:
            # Delete existing data for the specific year and rating type
            store_raw_data(all_data, f'{rating_type}_ratings', if_exists='replace', year=year)
            print(f"Successfully stored {rating_type.upper()} ratings data for year {year}")


def fetch_all_ratings(start_year, end_year, ratings_api, use_last_season=True):
    last_season = get_last_update('games') if use_last_season else None
    
    # Set minimum year to 2004
    MIN_YEAR = 2004
    start_year = max(start_year, MIN_YEAR)
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for rating_type in ['elo', 'fpi', 'sp', 'srs']:
        fetch_ratings(start_year, end_year, ratings_api, rating_type)
    print("Finished fetching all ratings data")


def fetch_pregame_win_probabilities(start_year, end_year, metrics_api, use_last_season=True):
    last_season = get_last_update('pregame_win_probabilities') if use_last_season else None
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = last_season
    
    for year in range(start_year, end_year + 1):
        year_probabilities = []
        for season_type in ['regular', 'postseason']:
            try:
                probabilities = metrics_api.get_pregame_win_probabilities(
                    year=year,
                    season_type=season_type
                )
                year_probabilities.extend([prob.to_dict() for prob in probabilities])
                print(f"Successfully fetched pregame win probabilities for {year} {season_type} season")
            except ApiException as e:
                print(f"Exception when calling MetricsApi->get_pregame_win_probabilities for year {year} {season_type} season: {e}\n")
            
            time.sleep(1)  # Add a delay to avoid hitting rate limits
        
        if year_probabilities:
            # Update or append data for this specific year
            store_raw_data(year_probabilities, 'pregame_win_probabilities', year=year)
            print(f"Updated/Appended pregame win probabilities data for year {year}")

    print("Finished fetching pregame win probabilities data")

def fetch_team_recruiting(start_year, end_year, recruiting_api, use_last_season=True):
    last_year = get_last_update('games') if use_last_season else None
    
    # If we have data, start from the last year
    if last_year is not None:
        start_year = last_year
    
    for year in range(start_year, end_year + 1):
        try:
            recruiting_data = recruiting_api.get_recruiting_teams(year=year)
            team_recruiting = [data.to_dict() for data in recruiting_data]
            
            if year == last_year:
                # Replace data for the last year
                store_raw_data(team_recruiting, 'team_recruiting', if_exists='replace')
                print(f"Replaced team recruiting data for year {year}")
            else:
                # Append data for new years
                store_raw_data(team_recruiting, 'team_recruiting', if_exists='append')
                print(f"Appended team recruiting data for year {year}")
            
            print(f"Successfully fetched team recruiting data for {year}")
        except ApiException as e:
            print(f"Exception when calling RecruitingApi->get_recruiting_teams for year {year}: {e}\n")
        
        time.sleep(1)  # Add a delay to avoid hitting rate limits
    
    print("Finished fetching team recruiting data")

def fetch_betting_lines(start_year, end_year, betting_api, use_last_season=True):
    last_season = get_last_update('betting_lines') if use_last_season else None
    
    # If we have data, start from the last season
    if last_season is not None:
        start_year = max(last_season, 2013)
    else:
        start_year = max(start_year, 2013)
    
    for year in range(start_year, end_year + 1):
        year_lines = []
        for season_type in ['regular', 'postseason']:
            try:
                lines = betting_api.get_lines(
                    year=year,
                    season_type=season_type
                )
                year_lines.extend([line.to_dict() for line in lines])
                print(f"Successfully fetched betting lines for {year} {season_type} season")
            except ApiException as e:
                print(f"Exception when calling BettingApi->get_lines for year {year} {season_type} season: {e}\n")
            
            time.sleep(1)  # Add a delay to avoid hitting rate limits
        
        if year_lines:
            # Update or append data for this specific year
            store_raw_data(year_lines, 'betting_lines', year=year)
            print(f"Updated/Appended betting lines data for year {year}")

    print("Finished fetching betting lines data")