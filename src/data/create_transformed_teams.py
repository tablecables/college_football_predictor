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

    # SQL query
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
    advanced_team_game_stats_deduped AS (
        SELECT DISTINCT *
        FROM advanced_team_game_stats
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
            home_id AS team_id,
            away_team AS opponent,
            away_id AS opponent_id,
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
            away_id AS team_id,
            home_team AS opponent,
            home_id AS opponent_id,
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

    SELECT DISTINCT
        -- Combined Game Data --
        cgd.*,
        
        -- Team Game Stats --
        CAST(tgs.fumblesRecovered AS INTEGER) AS fumblesRecovered,
        CAST(tgs.rushingTDs AS INTEGER) AS rushingTDs,
        CAST(tgs.puntReturnYards AS INTEGER) AS puntReturnYards,
        CAST(tgs.puntReturnTDs AS INTEGER) AS puntReturnTDs,
        CAST(tgs.puntReturns AS INTEGER) AS puntReturns,
        CAST(tgs.passingTDs AS INTEGER) AS passingTDs,
        CAST(tgs.kickingPoints AS INTEGER) AS kickingPoints,
        CAST(tgs.firstDowns AS INTEGER) AS firstDowns,
        tgs.thirdDownEff,
        tgs.fourthDownEff,
        CAST(tgs.totalYards AS INTEGER) AS totalYards,
        CAST(tgs.netPassingYards AS INTEGER) AS netPassingYards,
        tgs.completionAttempts,
        CAST(tgs.yardsPerPass AS REAL) AS yardsPerPass,
        CAST(tgs.rushingYards AS INTEGER) AS rushingYards,
        CAST(tgs.rushingAttempts AS INTEGER) AS rushingAttempts,
        CAST(tgs.yardsPerRushAttempt AS REAL) AS yardsPerRushAttempt,
        CAST(tgs.totalPenaltiesYards AS INTEGER) AS totalPenaltiesYards,
        CAST(tgs.turnovers AS INTEGER) AS turnovers,
        CAST(tgs.fumblesLost AS INTEGER) AS fumblesLost,
        CAST(tgs.interceptions AS INTEGER) AS interceptions,
        tgs.possessionTime,
        CAST(tgs.interceptionYards AS INTEGER) AS interceptionYards,
        CAST(tgs.interceptionTDs AS INTEGER) AS interceptionTDs,
        CAST(tgs.passesIntercepted AS INTEGER) AS passesIntercepted,
        CAST(tgs.kickReturnYards AS INTEGER) AS kickReturnYards,
        CAST(tgs.kickReturnTDs AS INTEGER) AS kickReturnTDs,
        CAST(tgs.kickReturns AS INTEGER) AS kickReturns,
        CAST(tgs.totalFumbles AS INTEGER) AS totalFumbles,
        CAST(tgs.tacklesForLoss AS INTEGER) AS tacklesForLoss,
        CAST(tgs.defensiveTDs AS INTEGER) AS defensiveTDs,
        CAST(tgs.tackles AS INTEGER) AS tackles,
        CAST(tgs.sacks AS INTEGER) AS sacks,
        CAST(tgs.qbHurries AS INTEGER) AS qbHurries,
        CAST(tgs.passesDeflected AS INTEGER) AS passesDeflected,
        
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
        ON cgd.id = tgs.id AND cgd.team_id = tgs.school_id
    LEFT JOIN advanced_team_game_stats_deduped adv
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
    
    -- WHERE cgd.year >= 2004
    """

    # Execute the query and fetch results
    source_cursor.execute(query)
    results = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

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