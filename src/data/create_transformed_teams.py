# college_football to transformed_teams.db

import sqlite3
import os

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
            season,
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
            season,
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
    )

    SELECT 
        cgd.*,
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
        tgs.passesDeflected
    FROM combined_game_data cgd
    LEFT JOIN team_game_stats_deduped tgs
        ON cgd.id = tgs.id AND cgd.team = tgs.team
    LEFT JOIN advanced_team_game_stats adv
        ON cgd.id = adv.game_id AND cgd.team = adv.team

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