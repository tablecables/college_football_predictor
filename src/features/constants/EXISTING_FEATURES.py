EXISTING_FEATURES = [
    # Existing features
    {
        "name": "year",
        "description": "Year of the game",
        "type": "existing"
    },
    {
        "name": "week",
        "description": "Week number of the game in the season",
        "type": "existing"
    },
    {
        "name": "start_date",
        "description": "Game date and time",
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
    }
]