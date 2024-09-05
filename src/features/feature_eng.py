# feature engineering

import pandas as pd
import numpy as np

POST_GAME_STATS = [
    # Basic Stats
    {
        "name": "totalYards",
        "description": "Total yards gained by the team"
    },
    {
        "name": "firstDowns",
        "description": "Number of first downs achieved"
    },
    {
        "name": "possessionTime",
        "description": "Time of possession in seconds"
    },
    {
        "name": "thirdDownPct",
        "description": "Percentage of successful third down conversions"
    },
    {
        "name": "fourthDownPct",
        "description": "Percentage of successful fourth down conversions"
    },
    {
        "name": "passingTDs",
        "description": "Number of passing touchdowns"
    },
    {
        "name": "netPassingYards",
        "description": "Net yards gained from passing"
    },
    {
        "name": "completionPct",
        "description": "Number of pass completions per attempts"
    },
    {
        "name": "yardsPerPass",
        "description": "Average yards gained per pass attempt"
    },
    {
        "name": "rushingTDs",
        "description": "Number of rushing touchdowns"
    },
    {
        "name": "rushingYards",
        "description": "Total rushing yards"
    },
    {
        "name": "rushingAttempts",
        "description": "Number of rushing attempts"
    },
    {
        "name": "yardsPerRushAttempt",
        "description": "Average yards gained per rush attempt"
    },
    {
        "name": "puntReturns",
        "description": "Number of punt returns"
    },
    {
        "name": "puntReturnYards",
        "description": "Total yards gained from punt returns"
    },
    {
        "name": "puntReturnTDs",
        "description": "Number of touchdowns scored on punt returns"
    },
    {
        "name": "kickingPoints",
        "description": "Total points scored from kicking (field goals and extra points)"
    },
    {
        "name": "penalties",
        "description": "Total number of penalties"
    },
    {
        "name": "penaltyYards",
        "description": "Total number of yards awarded to opponent from penalties"
    },
    {
        "name": "turnovers",
        "description": "Total number of turnovers"
    },
    {
        "name": "interceptions",
        "description": "Number of interceptions thrown"
    },
    {
        "name": "interceptionYards",
        "description": "Yards gained from interception returns"
    },
    {
        "name": "interceptionTDs",
        "description": "Number of touchdowns scored on interception returns"
    },
    {
        "name": "passesIntercepted",
        "description": "Number of passes intercepted by the defense"
    },
    {
        "name": "totalFumbles",
        "description": "Total number of fumbles"
    },
    {
        "name": "fumblesLost",
        "description": "Number of fumbles lost to the opposing team"
    },
    {
        "name": "fumblesRecovered",
        "description": "Number of fumbles recovered"
    },

    # Advanced Stats
    {
        "name": "offense_drives",
        "description": "Total number of offensive possessions",
    },
    {
        "name": "defense_drives",
        "description": "Total number of defensive possessions" 
    },
    {
        "name": "offense_explosiveness",
        "description": "How frequently a team generates big plays, typically runs of 12+ yards or passes of 15+ yards"  
    },
    {
        "name": "defense_explosiveness",
        "description": "How frequently a team generates big plays, typically runs of 12+ yards or passes of 15+ yards" 
    },
    {
        "name": "offense_line_yards",
        "description": "Measure of offensive line performance in run blocking"
    },
    {
        "name": "defense_line_yards",
        "description": "Measure of defensive line performance against the run"
    },
    {
        "name": "offense_open_field_yards",
        "description": "Yards gained by running backs beyond the first 10 yards of a run"
    },
    {
        "name": "defense_open_field_yards",
        "description": "Yards allowed by defense beyond the first 10 yards of a run"
    },
    {
        "name": "offense_power_success",
        "description": "Success rate on runs on third or fourth down with 2 yards or less to go"
    },
    {
        "name": "defense_power_success",
        "description": "Success rate allowed on runs on third or fourth down with 2 yards or less to go"
    },
    {
        "name": "offense_ppa",
        "description": "Predicted Points Added per play for offense"
    },
    {
        "name": "defense_ppa",
        "description": "Predicted Points Added per play allowed by defense"
    },
    {
        "name": "offense_second_level_yards",
        "description": "Yards gained by running backs between 5-10 yards past the line of scrimmage"
    },
    {
        "name": "defense_second_level_yards",
        "description": "Yards allowed by defense between 5-10 yards past the line of scrimmage"
    },
    {
        "name": "offense_stuff_rate",
        "description": "Percentage of runs where the running back is tackled at or behind the line of scrimmage"
    },
    {
        "name": "defense_stuff_rate",
        "description": "Percentage of runs where the defense tackles the running back at or behind the line of scrimmage"
    },
    {
        "name": "offense_success_rate",
        "description": "Percentage of plays that are considered successful (50% of needed yards on 1st down, 70% on 2nd, 100% on 3rd/4th)"
    },
    {
        "name": "defense_success_rate",
        "description": "Percentage of plays allowed that are considered successful for the offense"
    },
    {
        "name": "offense_total_ppa",
        "description": "Total Predicted Points Added for all offensive plays"
    },
    {
        "name": "defense_total_ppa",
        "description": "Total Predicted Points Added allowed for all defensive plays"
    },
    {
        "name": "offense_passing_downs.explosiveness",
        "description": "Explosiveness of offensive plays on passing downs"
    },
    {
        "name": "defense_passing_downs.explosiveness",
        "description": "Explosiveness allowed on plays during passing downs"
    },
    {
        "name": "offense_passing_downs.ppa",
        "description": "Predicted Points Added per play on passing downs"
    },
    {
        "name": "defense_passing_downs.ppa",
        "description": "Predicted Points Added allowed per play on passing downs"
    },
    {
        "name": "offense_passing_downs.success_rate",
        "description": "Success rate of offensive plays on passing downs"
    },
    {
        "name": "defense_passing_downs.success_rate",
        "description": "Success rate allowed on plays during passing downs"
    },
    {
        "name": "offense_passing_plays.explosiveness",
        "description": "Explosiveness of all offensive passing plays"
    },
    {
        "name": "defense_passing_plays.explosiveness",
        "description": "Explosiveness allowed on all passing plays"
    },
    {
        "name": "offense_passing_plays.ppa",
        "description": "Predicted Points Added per passing play"
    },
    {
        "name": "defense_passing_plays.ppa",
        "description": "Predicted Points Added allowed per passing play"
    },
    {
        "name": "offense_passing_plays.success_rate",
        "description": "Success rate of all offensive passing plays"
    },
    {
        "name": "defense_passing_plays.success_rate",
        "description": "Success rate allowed on all passing plays"
    },
    {
        "name": "offense_passing_plays.total_ppa",
        "description": "Total Predicted Points Added for all offensive passing plays"
    },
    {
        "name": "defense_passing_plays.total_ppa",
        "description": "Total Predicted Points Added allowed for all passing plays"
    },
    {
        "name": "offense_rushing_plays.explosiveness",
        "description": "Explosiveness of offensive rushing plays"
    },
    {
        "name": "defense_rushing_plays.explosiveness",
        "description": "Explosiveness allowed on rushing plays"
    },
    {
        "name": "offense_rushing_plays.ppa",
        "description": "Predicted Points Added per rushing play"
    },
    {
        "name": "defense_rushing_plays.ppa",
        "description": "Predicted Points Added allowed per rushing play"
    },
    {
        "name": "offense_rushing_plays.success_rate",
        "description": "Success rate of offensive rushing plays"
    },
    {
        "name": "defense_rushing_plays.success_rate",
        "description": "Success rate allowed on rushing plays"
    },
    {
        "name": "offense_rushing_plays.total_ppa",
        "description": "Total Predicted Points Added for all offensive rushing plays"
    },
    {
        "name": "defense_rushing_plays.total_ppa",
        "description": "Total Predicted Points Added allowed for all rushing plays"
    },
    {
        "name": "offense_standard_downs.explosiveness",
        "description": "Explosiveness of offensive plays on standard downs"
    },
    {
        "name": "defense_standard_downs.explosiveness",
        "description": "Explosiveness allowed on plays during standard downs"
    },
    {
        "name": "offense_standard_downs.ppa",
        "description": "Predicted Points Added per play on standard downs"
    },
    {
        "name": "defense_standard_downs.ppa",
        "description": "Predicted Points Added allowed per play on standard downs"
    },
    {
        "name": "offense_standard_downs.success_rate",
        "description": "Success rate of offensive plays on standard downs"
    },
    {
        "name": "defense_standard_downs.success_rate",
        "description": "Success rate allowed on plays during standard downs"
    }
]

ENGINEERED_FEATURES = [
    {
        "base_name": stat["name"],
        "description": stat["description"],
        "type": "engineered",
        "variants": [
            {"suffix": "last_3", "function": "calculate_rolling_average", "params": {"n": 3}},
            {"suffix": "last_10", "function": "calculate_rolling_average", "params": {"n": 10}},
            {"suffix": "weighted", "function": "calculate_weighted_average"}
        ]
    } for stat in POST_GAME_STATS
] + [
    {
        "name": "win_rate_last_1",
        "description": "Result of their last game",
        "type": "engineered",
        "function": "calculate_win_rate_last_n",
        "params": {"n": 1}
    },
    {
        "name": "win_rate_last_3",
        "description": "Win rate of the team in their last 3 games",
        "type": "engineered",
        "function": "calculate_win_rate_last_n",
        "params": {"n": 3}
    },
    {
        "name": "win_rate_last_5",
        "description": "Win rate of the team in their last 5 games",
        "type": "engineered",
        "function": "calculate_win_rate_last_n",
        "params": {"n": 5}
    },
    {
        "name": "win_rate_last_10",
        "description": "Win rate of the team in their last 10 games",
        "type": "engineered",
        "function": "calculate_win_rate_last_n",
        "params": {"n": 10}
    },
    {
        "name": "points_scored_last_1",
        "description": "Average points scored in the last 1 games",
        "type": "engineered",
        "function": "calculate_total_points_last_n",
        "params": {"stat": "team_points", "n": 1}
    },
    {
        "name": "points_allowed_last_1",
        "description": "Average points allowed in the last 1 games",
        "type": "engineered",
        "function": "calculate_total_points_last_n",
        "params": {"stat": "opponent_points", "n": 1}
    },
    {
        "name": "points_scored_last_3",
        "description": "Average points scored in the last 3 games",
        "type": "engineered",
        "function": "calculate_total_points_last_n",
        "params": {"stat": "team_points", "n": 3}
    },
    {
        "name": "points_allowed_last_3",
        "description": "Average points allowed in the last 3 games",
        "type": "engineered",
        "function": "calculate_total_points_last_n",
        "params": {"stat": "opponent_points", "n": 3}
    },
]

FEATURES = [
    # Existing features
    {
        "name": "season",
        "description": "Year of the game",
        "type": "existing"
    },
    {
        "name": "week",
        "description": "Week number of the game in the season",
        "type": "existing"
    },
    {
        "name": "is_home",
        "description": "Whether the team is playing at home",
        "type": "existing"
    },
    {
        "name": "season_type",
        "description": "Regular or post season",
        "type": "existing",
        "categorical": True
    },
    {
        "name": "neutral_site",
        "description": "Whether one of the teams is playing at home or not",
        "type": "existing"
    },
    {
        "name": "conference_game",
        "description": "If the matchup is within the conference or not",
        "type": "existing"
    },
    {
        "name": "team_id",
        "description": "Unique identifier for each team",
        "type": "existing",
        "categorical": True
    },
    {
        "name": "opponent_id",
        "description": "Unique identifier for each opponent" ,
        "type": "existing",
        "categorical": True
    },
    {
        "name": "team_conference",
        "description": "Team conference",
        "type": "existing",
        "categorical": True
    },
    {
        "name": "opponent_conference",
        "description": "Opponent's conference",
        "type": "existing",
        "categorical": True
    },
    {
        "name": "win",
        "description": "Did the team win?",
        "type": "existing"
    },
    {
        "name": "start_date",
        "description": "Game date and time",
        "type": "existing"
    }
] + ENGINEERED_FEATURES

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
        return [f["name"] for f in FEATURES if f["type"] == feature_type]
    return [f["name"] for f in FEATURES if f["type"] == "existing"] + get_feature_names("engineered")
