# feature engineering

POST_GAME_STATS = [
    # Basic Stats
    {
        "name": "total_yards",
        "description": "Total yards gained by the team"
    },
    {
        "name": "first_downs",
        "description": "Number of first downs achieved"
    },
    {
        "name": "possession_time",
        "description": "Time of possession in seconds"
    },
    {
        "name": "third_down_efficiency",
        "description": "Percentage of successful third down conversions"
    },
    {
        "name": "fourth_down_efficiency",
        "description": "Percentage of successful fourth down conversions"
    },
    {
        "name": "passing_touchdowns",
        "description": "Number of passing touchdowns"
    },
    {
        "name": "net_passing_yards",
        "description": "Net yards gained from passing"
    },
    {
        "name": "completion_attempts",
        "description": "Number of pass completions and attempts"
    },
    {
        "name": "yards_per_pass",
        "description": "Average yards gained per pass attempt"
    },
    {
        "name": "rushing_touchdowns",
        "description": "Number of rushing touchdowns"
    },
    {
        "name": "rushing_yards",
        "description": "Total rushing yards"
    },
    {
        "name": "rushing_attempts",
        "description": "Number of rushing attempts"
    },
    {
        "name": "yards_per_rush_attempt",
        "description": "Average yards gained per rush attempt"
    },
    {
        "name": "punt_returns",
        "description": "Number of punt returns"
    },
    {
        "name": "punt_return_yards",
        "description": "Total yards gained from punt returns"
    },
    {
        "name": "punt_return_touchdowns",
        "description": "Number of touchdowns scored on punt returns"
    },
    {
        "name": "kicking_points",
        "description": "Total points scored from kicking (field goals and extra points)"
    },
    {
        "name": "total_penalties_yards",
        "description": "Total yards penalized"
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
        "name": "interception_yards",
        "description": "Yards gained from interception returns"
    },
    {
        "name": "interception_touchdowns",
        "description": "Number of touchdowns scored on interception returns"
    },
    {
        "name": "passes_intercepted",
        "description": "Number of passes intercepted by the defense"
    },
    {
        "name": "total_fumbles",
        "description": "Total number of fumbles"
    },
    {
        "name": "fumbles_lost",
        "description": "Number of fumbles lost to the opposing team"
    },
    {
        "name": "fumbles_recovered",
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
            {"suffix": "season_to_date", "function": "calculate_season_average"},
            {"suffix": "weighted", "function": "calculate_weighted_average"}
        ]
    } for stat in POST_GAME_STATS
] + [
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
        "name": "win_rate_season",
        "description": "Win rate of the team in the current season",
        "type": "engineered",
        "function": "calculate_season_win_rate"
    },
    {
        "name": "points_scored_last_3",
        "description": "Average points scored in the last 3 games",
        "type": "engineered",
        "function": "calculate_rolling_average",
        "params": {"stat": "points", "n": 3}
    },
    {
        "name": "points_allowed_last_3",
        "description": "Average points allowed in the last 3 games",
        "type": "engineered",
        "function": "calculate_rolling_average",
        "params": {"stat": "opponent_points", "n": 3}
    },
    {
        "name": "point_differential_season",
        "description": "Average point differential for the season",
        "type": "engineered",
        "function": "calculate_season_point_differential"
    }
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
    }
] + ENGINEERED_FEATURES


def get_feature_names(feature_type=None):
    if feature_type == "engineered":
        return [f"{feature['base_name']}_{variant['suffix']}" 
                for feature in FEATURES if feature['type'] == "engineered"
                for variant in feature['variants']]
    elif feature_type:
        return [f["name"] for f in FEATURES if f["type"] == feature_type]
    return [f["name"] for f in FEATURES if "name" in f] + get_feature_names("engineered")

# You'll need to implement these functions:
def calculate_rolling_average(data, stat, n):
    # Calculate rolling average for last n games
    pass

def calculate_season_average(data, stat):
    # Calculate average for the current season
    pass

def calculate_weighted_average(data, stat):
    # Calculate weighted average, giving more weight to recent games
    pass

def calculate_win_rate_last_n(data, n):
    # Calculate win rate for last n games
    pass

def calculate_season_win_rate(data):
    # Calculate win rate for the current season
    pass

def calculate_season_point_differential(data):
    # Calculate average point differential for the season
    pass

# Modify the get_engineered_feature_functions to handle the new structure
def get_engineered_feature_functions():
    return {feature['name']: globals()[feature['function']]
            for feature in ENGINEERED_FEATURES if feature['type'] == "engineered"}