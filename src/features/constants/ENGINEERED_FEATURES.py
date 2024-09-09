from .RAW_FEATURES import RAW_FEATURES

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
    } for stat in RAW_FEATURES
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