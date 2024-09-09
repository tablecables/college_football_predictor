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