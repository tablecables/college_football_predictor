# Create Processed Teams

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

def create_processed_teams_db(source_db_path, target_db_path):
    print(f"Source DB path: {source_db_path}")
    print(f"Target DB path: {target_db_path}")
    
    # Connect to the source and target databases
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()
    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()

    # Check if the transformed_teams table exists in the source database
    source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transformed_teams';")
    if not source_cursor.fetchone():
        raise ValueError("transformed_teams table not found in the source database")

    # SQL query to clean and process the data
    clean_data_query = """
    WITH team_info AS (
        SELECT team, 
               MAX(team_conference) AS team_conference, 
               MAX(team_division) AS team_division
        FROM transformed_teams
        WHERE team_conference IS NOT NULL AND team_conference != ''
          AND team_division IS NOT NULL AND team_division != ''
        GROUP BY team
    ),
    cleaned_data AS (
        SELECT t.*,
            COALESCE(t.team_conference, ti.team_conference, 'Unknown') AS team_conference,
            COALESCE(t.team_division, ti.team_division, 'Unknown') AS team_division,
            COALESCE(t.opponent_conference, oi.team_conference, 'Unknown') AS opponent_conference,
            COALESCE(t.opponent_division, oi.team_division, 'Unknown') AS opponent_division,
            CASE 
                WHEN attendance = 0 THEN NULL
                ELSE attendance
            END AS cleaned_attendance,
            CASE 
                WHEN possessionTime IS NULL THEN NULL
                WHEN possessionTime LIKE '%:%' THEN 
                    CAST(SUBSTR(possessionTime, 1, INSTR(possessionTime, ':') - 1) AS FLOAT) +
                    CAST(SUBSTR(possessionTime, INSTR(possessionTime, ':') + 1) AS FLOAT) / 60.0
                ELSE CAST(possessionTime AS FLOAT) / 60.0
            END AS possession_time_minutes,
            CAST(SUBSTR(thirdDownEff, 1, INSTR(thirdDownEff, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(thirdDownEff, INSTR(thirdDownEff, '-') + 1) AS FLOAT) AS thirdDownPct,
            CAST(SUBSTR(fourthDownEff, 1, INSTR(fourthDownEff, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(fourthDownEff, INSTR(fourthDownEff, '-') + 1) AS FLOAT) AS fourthDownPct,
            CAST(SUBSTR(completionAttempts, 1, INSTR(completionAttempts, '-') - 1) AS FLOAT) / 
                CAST(SUBSTR(completionAttempts, INSTR(completionAttempts, '-') + 1) AS FLOAT) AS completionPct,
            CAST(SUBSTR(totalPenaltiesYards, 1, INSTR(totalPenaltiesYards, '-') - 1) AS INTEGER) AS penalties,
            CAST(SUBSTR(totalPenaltiesYards, INSTR(totalPenaltiesYards, '-') + 1) AS INTEGER) AS penaltyYards
        FROM transformed_teams t
        LEFT JOIN team_info ti ON t.team = ti.team
        LEFT JOIN team_info oi ON t.opponent = oi.team
    ),
    yearly_avg_excitement AS (
    SELECT year, AVG(excitement_index) AS avg_excitement
    FROM cleaned_data
    WHERE excitement_index IS NOT NULL
        GROUP BY year
    )
    SELECT 
        id, year, week, season_type, start_date, neutral_site,
        COALESCE(conference_game, 
            CASE 
                WHEN team_conference = opponent_conference THEN 1
                ELSE 0
            END
        ) AS conference_game,
        COALESCE(cleaned_attendance, 
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year AND c2.venue_id = cleaned_data.venue_id),
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c3 
             WHERE c3.year = cleaned_data.year AND c3.team = cleaned_data.team),
            (SELECT AVG(cleaned_attendance) FROM cleaned_data c4 
             WHERE c4.year = cleaned_data.year)
        ) AS attendance,
        COALESCE(venue_id, -1) AS venue_id,
        COALESCE(venue, 'Unknown Venue') AS venue,
        team_id, team, team_conference, team_division, team_points,
        opponent_id, opponent, opponent_conference, opponent_division, opponent_points,
        CAST(home_away = 'home' AS INTEGER) AS is_home,
        CASE 
        WHEN year > 2013 AND start_date < DATE('now') AND excitement_index IS NULL THEN 
            (SELECT avg_excitement 
             FROM yearly_avg_excitement y 
             WHERE y.year = cleaned_data.year)
            ELSE excitement_index
        END AS excitement_index,
        COALESCE(fumblesLost, 0) + COALESCE(fumblesRecovered, 0) AS totalFumbles,
        COALESCE(puntReturnYards, 0) AS puntReturnYards,
        COALESCE(puntReturnTDs, 0) AS puntReturnTDs,
        COALESCE(puntReturns, 0) AS puntReturns,
        COALESCE(kickingPoints, 0) AS kickingPoints,
        COALESCE(interceptionYards, 0) AS interceptionYards,
        COALESCE(interceptionTDs, 0) AS interceptionTDs,
        COALESCE(passesIntercepted, 0) AS passesIntercepted,
        COALESCE(passingTDs, 0) AS passingTDs,
        COALESCE(rushingTDs, 0) AS rushingTDs,
        COALESCE(penalties, 0) AS penalties,
        COALESCE(penaltyYards, 0) AS penaltyYards,
        COALESCE(possession_time_minutes, 
            (SELECT AVG(possession_time_minutes) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year AND c2.team = cleaned_data.team),
            (SELECT AVG(possession_time_minutes) FROM cleaned_data)
        ) AS possessionMinutes,
        COALESCE(thirdDownPct, 
            (SELECT AVG(thirdDownPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS thirdDownPct,
        COALESCE(fourthDownPct, 
            (SELECT AVG(fourthDownPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS fourthDownPct,
        COALESCE(completionPct, 
            (SELECT AVG(completionPct) FROM cleaned_data c2 
             WHERE c2.year = cleaned_data.year)) AS completionPct,
        CASE 
            WHEN year < 2015 THEN NULL
            ELSE COALESCE(
                team_talent,
                (SELECT AVG(c2.team_talent) FROM cleaned_data c2 
                 WHERE c2.year = cleaned_data.year 
                 AND c2.team_conference = cleaned_data.team_conference
                 AND c2.team_talent IS NOT NULL),
                (SELECT AVG(c3.team_talent) FROM cleaned_data c3 
                 WHERE c3.year = cleaned_data.year
                 AND c3.team_talent IS NOT NULL)
            )
        END AS team_talent,
        CASE 
            WHEN year < 2015 THEN NULL
            ELSE COALESCE(
                opponent_talent,
                (SELECT AVG(c2.team_talent) FROM cleaned_data c2 
                 WHERE c2.year = cleaned_data.year 
                 AND c2.team_conference = cleaned_data.opponent_conference
                 AND c2.team_talent IS NOT NULL),
                (SELECT AVG(c3.team_talent) FROM cleaned_data c3 
                 WHERE c3.year = cleaned_data.year
                 AND c3.team_talent IS NOT NULL)
            )
        END AS opponent_talent,
        team_points - opponent_points AS point_difference,
        CASE 
            WHEN team_points > opponent_points THEN 'win'
            WHEN team_points < opponent_points THEN 'loss'
            ELSE 'tie'
        END AS result,
        CASE 
            WHEN team_points > opponent_points THEN 1
            WHEN team_points = opponent_points THEN 0.5
            ELSE 0
        END AS win
    FROM cleaned_data
    """

    # Execute the query and fetch results
    source_cursor.execute(clean_data_query)
    results = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Drop the existing table if it exists
    target_cursor.execute("DROP TABLE IF EXISTS processed_teams")

    # Create the table in the target database
    create_table_query = f"CREATE TABLE processed_teams ({', '.join(column_names)})"
    target_cursor.execute(create_table_query)

    # Insert the data into the target database
    insert_query = f"INSERT INTO processed_teams VALUES ({', '.join(['?' for _ in column_names])})"
    target_cursor.executemany(insert_query, results)

    # Commit changes and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print(f"Processed teams data has been written to {target_db_path}")

def load_processed_teams_df(db_path):
    """
    Load the processed_teams table from the SQLite database into a pandas DataFrame.

    Args:
    db_path (str): Path to the SQLite database file.

    Returns:
    pandas.DataFrame: DataFrame containing the processed_teams data.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM processed_teams"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_db_path = os.path.join(project_root, 'data', '02_interim', 'transformed_teams.db')
    target_db_path = os.path.join(project_root, 'data', '03_processed', 'processed_teams.db')
    
    create_processed_teams_db(source_db_path, target_db_path)
    
    # Load and display the processed data
    processed_teams_df = load_processed_teams_df(target_db_path)
    
    print(f"Loaded processed_teams data. Shape: {processed_teams_df.shape}")
    print(processed_teams_df.head())