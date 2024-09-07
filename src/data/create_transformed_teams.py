# college_football to transformed_teams.db

import sqlite3
import os
import pandas as pd

def create_transformed_teams_db(source_db_path, target_db_path):
    # Connect to the source database
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    # Connect to the target database (this will create it if it doesn't exist)
    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()

    # Your SQL query
    query = """

    WITH games_deduped AS (
        SELECT DISTINCT *
        FROM games
    ),
    team_game_stats_deduped AS (
        SELECT DISTINCT *,
            school AS team  -- Rename 'school' to 'team'
        FROM team_game_stats
    ),
    team_talent_deduped AS (
        SELECT DISTINCT *
        FROM team_talent
    ),
    home_team_data AS (
        SELECT
            id,
            season AS year,
            week,
            season_type,
            start_date,
            completed,
            neutral_site,
            conference_game,
            attendance,
            venue_id,
            venue,
            home_team AS team,
            away_team AS opponent,
            home_conference AS team_conference,
            away_conference AS opponent_conference,
            home_division AS team_division,
            away_division AS opponent_division,
            home_points AS team_points,
            away_points AS opponent_points,
            home_line_scores AS team_line_scores,
            away_line_scores AS opponent_line_scores,
            home_post_win_prob AS team_post_win_prob,
            away_post_win_prob AS opponent_post_win_prob,
            excitement_index,
            home_pregame_elo AS team_pregame_elo,
            away_pregame_elo AS opponent_pregame_elo,
            home_postgame_elo AS team_postgame_elo,
            away_postgame_elo AS opponent_postgame_elo,
            'home' AS home_away
        FROM games_deduped
    ),
    away_team_data AS (
        SELECT 
            id,
            season AS year,
            week,
            season_type,
            start_date,
            completed,
            neutral_site,
            conference_game,
            attendance,
            venue_id,
            venue,
            away_team AS team,
            home_team AS opponent,
            away_conference AS team_conference,
            home_conference AS opponent_conference,
            away_division AS team_division,
            home_division AS opponent_division,
            away_points AS team_points,
            home_points AS opponent_points,
            away_line_scores AS team_line_scores,
            home_line_scores AS opponent_line_scores,
            away_post_win_prob AS team_post_win_prob,
            home_post_win_prob AS opponent_post_win_prob,
            excitement_index,
            away_pregame_elo AS team_pregame_elo,
            home_pregame_elo AS opponent_pregame_elo,
            away_postgame_elo AS team_postgame_elo,
            home_postgame_elo AS opponent_postgame_elo,
            'away' AS home_away
        FROM games_deduped
    ),
    combined_game_data AS (
        SELECT * FROM home_team_data
        UNION ALL
        SELECT * FROM away_team_data
    ),
    home_betting_lines AS (
        SELECT
            id,
            home_team AS team,
            AVG(line_spread) AS avg_line_spread,
            AVG(line_spread_open) AS avg_line_spread_open,
            AVG(line_over_under) AS avg_line_over_under,
            AVG(line_over_under_open) AS avg_line_over_under_open,
            AVG(line_home_moneyline) AS avg_line_team_moneyline,
            AVG(line_away_moneyline) AS avg_line_opponent_moneyline
        FROM betting_lines
        GROUP BY id, home_team
    ),
    away_betting_lines AS (
        SELECT
            id,
            away_team AS team,
            AVG(-line_spread) AS avg_line_spread,
            AVG(-line_spread_open) AS avg_line_spread_open,
            AVG(line_over_under) AS avg_line_over_under,
            AVG(line_over_under_open) AS avg_line_over_under_open,
            AVG(line_away_moneyline) AS avg_line_team_moneyline,
            AVG(line_home_moneyline) AS avg_line_opponent_moneyline
        FROM betting_lines
        GROUP BY id, away_team
    )

    SELECT 
        -- Combined Game Data --
        cgd.*,
        
        -- Team Game Stats --
        tgs.school_id as team_id,
        tgs.fumblesRecovered,
        tgs.rushingTDs,
        tgs.puntReturnYards,
        tgs.puntReturnTDs,
        tgs.puntReturns,
        tgs.passingTDs,
        tgs.kickingPoints,
        tgs.firstDowns,
        tgs.thirdDownEff,
        tgs.fourthDownEff,
        tgs.totalYards,
        tgs.netPassingYards,
        tgs.completionAttempts,
        tgs.yardsPerPass,
        tgs.rushingYards,
        tgs.rushingAttempts,
        tgs.yardsPerRushAttempt,
        tgs.totalPenaltiesYards,
        tgs.turnovers,
        tgs.fumblesLost,
        tgs.interceptions,
        tgs.possessionTime,
        tgs.interceptionYards,
        tgs.interceptionTDs,
        tgs.passesIntercepted,
        tgs.kickReturnYards,
        tgs.kickReturnTDs,
        tgs.kickReturns,
        tgs.totalFumbles,
        tgs.tacklesForLoss,
        tgs.defensiveTDs,
        tgs.tackles,
        tgs.sacks,
        tgs.qbHurries,
        tgs.passesDeflected,
        
        -- Advanced Stats --
        adv.offense_plays,
        adv.offense_drives,
        adv.offense_ppa,
        adv.offense_total_ppa,
        adv.offense_success_rate,
        adv.offense_explosiveness,
        adv.offense_power_success,
        adv.offense_stuff_rate,
        adv.offense_line_yards,
        adv.offense_line_yards_total,
        adv.offense_second_level_yards,
        adv.offense_second_level_yards_total,
        adv.offense_open_field_yards,
        adv.offense_open_field_yards_total,
        adv.offense_standard_downs_ppa,
        adv.offense_standard_downs_success_rate,
        adv.offense_standard_downs_explosiveness,
        adv.offense_passing_downs_ppa,
        adv.offense_passing_downs_success_rate,
        adv.offense_passing_downs_explosiveness,
        adv.offense_rushing_plays_ppa,
        adv.offense_rushing_plays_total_ppa,
        adv.offense_rushing_plays_success_rate,
        adv.offense_rushing_plays_explosiveness,
        adv.offense_passing_plays_ppa,
        adv.offense_passing_plays_total_ppa,
        adv.offense_passing_plays_success_rate,
        adv.offense_passing_plays_explosiveness,
        adv.defense_plays,
        adv.defense_drives,
        adv.defense_ppa,
        adv.defense_total_ppa,
        adv.defense_success_rate,
        adv.defense_explosiveness,
        adv.defense_power_success,
        adv.defense_stuff_rate,
        adv.defense_line_yards,
        adv.defense_line_yards_total,
        adv.defense_second_level_yards,
        adv.defense_second_level_yards_total,
        adv.defense_open_field_yards,
        adv.defense_open_field_yards_total,
        adv.defense_standard_downs_ppa,
        adv.defense_standard_downs_success_rate,
        adv.defense_standard_downs_explosiveness,
        adv.defense_passing_downs_ppa,
        adv.defense_passing_downs_success_rate,
        adv.defense_passing_downs_explosiveness,
        adv.defense_rushing_plays_ppa,
        adv.defense_rushing_plays_total_ppa,
        adv.defense_rushing_plays_success_rate,
        adv.defense_rushing_plays_explosiveness,
        adv.defense_passing_plays_ppa,
        adv.defense_passing_plays_total_ppa,
        adv.defense_passing_plays_success_rate,
        adv.defense_passing_plays_explosiveness,
        
        -- Betting Lines --
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_spread
            ELSE abl.avg_line_spread
        END AS avg_line_spread,
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_spread_open
            ELSE abl.avg_line_spread_open
        END AS avg_line_spread_open,
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_over_under
            ELSE abl.avg_line_over_under
        END AS avg_line_over_under,
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_over_under_open
            ELSE abl.avg_line_over_under_open
        END AS avg_line_over_under_open,
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_team_moneyline
            ELSE abl.avg_line_team_moneyline
        END AS avg_line_team_moneyline,
        CASE WHEN cgd.home_away = 'home'
            THEN hbl.avg_line_opponent_moneyline
            ELSE abl.avg_line_opponent_moneyline
        END AS avg_line_opponent_moneyline,
        
        -- Elo Ratings --
        er_team.elo AS team_elo_rating,
        er_opponent.elo AS opponent_elo_rating,
        
        -- Pre-game Win Probabilities --
        CASE
            WHEN cgd.home_away = 'home' THEN pwp_home.home_win_prob
            ELSE 1 - pwp_home.home_win_prob
        END AS team_pregame_win_prob,
        
        -- Recruiting --
        tr.rank AS team_recruiting_rank,
        tr.points AS team_recruiting_points,
        tr_opponent.rank AS opponent_recruiting_rank,
        tr_opponent.points AS opponent_recruiting_points,
        
        -- Team Talent --
        tt.talent AS team_talent,
        tt_opponent.talent AS opponent_talent,

        -- Result --
        CASE
            WHEN cgd.team_points > cgd.opponent_points THEN 1
            WHEN cgd.team_points < cgd.opponent_points THEN 0
            ELSE 0.5
        END AS win

    FROM combined_game_data cgd
    LEFT JOIN team_game_stats_deduped tgs
        ON cgd.id = tgs.id AND cgd.team = tgs.team
    LEFT JOIN advanced_team_game_stats adv
        ON cgd.id = adv.game_id AND cgd.team = adv.team
    LEFT JOIN home_betting_lines hbl
        ON cgd.id = hbl.id AND cgd.team = hbl.team
    LEFT JOIN away_betting_lines abl
        ON cgd.id = abl.id AND cgd.team = abl.team
    LEFT JOIN elo_ratings er_team
        ON cgd.year = er_team.year AND cgd.team = er_team.team
    LEFT JOIN elo_ratings er_opponent
        ON cgd.year = er_opponent.year AND cgd.opponent = er_opponent.team
    LEFT JOIN pregame_win_probabilities pwp_home
        ON cgd.id = pwp_home.game_id AND cgd.team = pwp_home.home_team
    LEFT JOIN team_recruiting tr
        ON cgd.year = tr.year AND cgd.team = tr.team
    LEFT JOIN team_recruiting tr_opponent
        ON cgd.year = tr_opponent.year AND cgd.opponent = tr_opponent.team
    LEFT JOIN team_talent_deduped tt
        ON cgd.year = tt.year AND cgd.team = tt.school
    LEFT JOIN team_talent_deduped tt_opponent
        ON cgd.year = tt_opponent.year AND cgd.opponent = tt_opponent.school
    
    WHERE cgd.year >= 2004
    """

    # Execute the query and fetch results
    source_cursor.execute(query)
    results = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Define data types for columns
    column_types = {
        'id': 'INTEGER',
        'year': 'INTEGER',
        'week': 'INTEGER',
        'season_type': 'TEXT',
        'start_date': 'DATETIME',
        'completed': 'BOOLEAN',
        'neutral_site': 'BOOLEAN',
        'conference_game': 'BOOLEAN',
        'attendance': 'INTEGER',
        'venue_id': 'INTEGER',
        'venue': 'TEXT',
        'team': 'TEXT',
        'opponent': 'TEXT',
        'team_conference': 'TEXT',
        'opponent_conference': 'TEXT',
        'team_division': 'TEXT',
        'opponent_division': 'TEXT',
        'team_points': 'INTEGER',
        'opponent_points': 'INTEGER',
        'team_line_scores': 'TEXT', #! breakout?
        'opponent_line_scores': 'TEXT', #! breakout?
        'team_post_win_prob': 'REAL',
        'opponent_post_win_prob': 'REAL',
        'excitement_index': 'REAL',
        'team_pregame_elo': 'INTEGER',
        'opponent_pregame_elo': 'INTEGER',
        'team_postgame_elo': 'INTEGER',
        'opponent_postgame_elo': 'INTEGER',
        'home_away': 'TEXT',
        #! team_id null a lot, starts in 2004
        'team_id': 'INTEGER',
        'fumblesRecovered': 'INTEGER',
        'rushingTDs': 'INTEGER',
        'puntReturnYards': 'INTEGER',
        'puntReturnTDs': 'INTEGER',
        'puntReturns': 'INTEGER',
        'passingTDs': 'INTEGER',
        'kickingPoints': 'INTEGER',
        'firstDowns': 'INTEGER',
        'thirdDownEff': 'TEXT',
        'fourthDownEff': 'TEXT',
        'totalYards': 'INTEGER',
        'netPassingYards': 'INTEGER',
        'completionAttempts': 'TEXT',
        'yardsPerPass': 'REAL',
        'rushingYards': 'INTEGER',
        'rushingAttempts': 'INTEGER',
        'yardsPerRushAttempt': 'REAL',
        'totalPenaltiesYards': 'TEXT',
        'turnovers': 'INTEGER',
        'fumblesLost': 'INTEGER',
        'interceptions': 'INTEGER',
        'possessionTime': 'TEXT',
        'interceptionYards': 'INTEGER',
        'interceptionTDs': 'INTEGER',
        'passesIntercepted': 'INTEGER',
        'kickReturnYards': 'INTEGER',
        'kickReturnTDs': 'INTEGER',
        'kickReturns': 'INTEGER',
        'totalFumbles': 'INTEGER',
        'tacklesForLoss': 'INTEGER',
        'defensiveTDs': 'INTEGER',
        'tackles': 'INTEGER',
        'sacks': 'INTEGER',
        'qbHurries': 'INTEGER',
        'passesDeflected': 'INTEGER',
        'offense_plays': 'INTEGER',
        'offense_drives': 'INTEGER',
        'offense_ppa': 'REAL',
        'offense_total_ppa': 'REAL',
        'offense_success_rate': 'REAL',
        'offense_explosiveness': 'REAL',
        'offense_power_success': 'REAL',
        'offense_stuff_rate': 'REAL',
        'offense_line_yards': 'REAL',
        'offense_line_yards_total': 'REAL',
        'offense_second_level_yards': 'REAL',
        'offense_second_level_yards_total': 'REAL',
        'offense_open_field_yards': 'REAL',
        'offense_open_field_yards_total': 'REAL',
        'offense_standard_downs_ppa': 'REAL',
        'offense_standard_downs_success_rate': 'REAL',
        'offense_standard_downs_explosiveness': 'REAL',
        'offense_passing_downs_ppa': 'REAL',
        'offense_passing_downs_success_rate': 'REAL',
        'offense_passing_downs_explosiveness': 'REAL',
        'offense_rushing_plays_ppa': 'REAL',
        'offense_rushing_plays_total_ppa': 'REAL',
        'offense_rushing_plays_success_rate': 'REAL',
        'offense_rushing_plays_explosiveness': 'REAL',
        'offense_passing_plays_ppa': 'REAL',
        'offense_passing_plays_total_ppa': 'REAL',
        'offense_passing_plays_success_rate': 'REAL',
        'offense_passing_plays_explosiveness': 'REAL',
        'defense_plays': 'INTEGER',
        'defense_drives': 'INTEGER',
        'defense_ppa': 'REAL',
        'defense_total_ppa': 'REAL',
        'defense_success_rate': 'REAL',
        'defense_explosiveness': 'REAL',
        'defense_power_success': 'REAL',
        'defense_stuff_rate': 'REAL',
        'defense_line_yards': 'REAL',
        'defense_line_yards_total': 'REAL',
        'defense_second_level_yards': 'REAL',
        'defense_second_level_yards_total': 'REAL',
        'defense_open_field_yards': 'REAL',
        'defense_open_field_yards_total': 'REAL',
        'defense_standard_downs_ppa': 'REAL',
        'defense_standard_downs_success_rate': 'REAL',
        'defense_standard_downs_explosiveness': 'REAL',
        'defense_passing_downs_ppa': 'REAL',
        'defense_passing_downs_success_rate': 'REAL',
        'defense_passing_downs_explosiveness': 'REAL',
        'defense_rushing_plays_ppa': 'REAL',
        'defense_rushing_plays_total_ppa': 'REAL',
        'defense_rushing_plays_success_rate': 'REAL',
        'defense_rushing_plays_explosiveness': 'REAL',
        'defense_passing_plays_ppa': 'REAL',
        'defense_passing_plays_total_ppa': 'REAL',
        'defense_passing_plays_success_rate': 'REAL',
        'defense_passing_plays_explosiveness': 'REAL',
        'avg_line_spread': 'REAL',
        'avg_line_spread_open': 'REAL',
        'avg_line_over_under': 'REAL',
        'avg_line_over_under_open': 'REAL',
        'avg_line_team_moneyline': 'REAL',
        'avg_line_opponent_moneyline': 'REAL',
        'team_elo_rating': 'REAL',
        'opponent_elo_rating': 'REAL',
        'team_pregame_win_prob': 'REAL',
        'opponent_pregame_win_prob': 'REAL',
        'team_recruiting_rank': 'INTEGER',
        'team_recruiting_points': 'INTEGER',
        'opponent_recruiting_rank': 'INTEGER',
        'opponent_recruiting_points': 'INTEGER',
        'team_talent': 'REAL',
        'opponent_talent': 'REAL',
        'win': 'INTEGER'
    }

    # Drop the existing table if it exists
    target_cursor.execute("DROP TABLE IF EXISTS transformed_teams")

    # Create the table in the target database
    create_table_query = f"CREATE TABLE transformed_teams ({', '.join(column_names)})"
    target_cursor.execute(create_table_query)

    # Insert the data into the target database
    insert_query = f"INSERT INTO transformed_teams VALUES ({', '.join(['?' for _ in column_names])})"
    target_cursor.executemany(insert_query, results)

    # Commit changes and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print(f"Transformed teams data has been written to {target_db_path}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_db_path = os.path.join(project_root, 'data', '02_interim', 'college_football.db')
    target_db_path = os.path.join(project_root, 'data', '02_interim', 'transformed_teams.db')
    
    create_transformed_teams_db(source_db_path, target_db_path)

def load_transformed_teams_df(db_path):
    """
    Load the transformed_teams table from the SQLite database into a pandas DataFrame.

    Args:
    db_path (str): Path to the SQLite database file.

    Returns:
    pandas.DataFrame: DataFrame containing the transformed_teams data.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM transformed_teams"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_db_path = os.path.join(project_root, 'data', '02_interim', 'college_football.db')
    target_db_path = os.path.join(project_root, 'data', '02_interim', 'transformed_teams.db')
    
    create_transformed_teams_db(source_db_path, target_db_path)
    
    # Load the transformed_teams data into a DataFrame
    transformed_teams_df = load_transformed_teams_df(target_db_path)
    print(f"Loaded transformed_teams data. Shape: {transformed_teams_df.shape}")
    print(transformed_teams_df.head())