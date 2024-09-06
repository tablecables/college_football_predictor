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
    SELECT 
        tgs.*,
        -- Add columns from advanced_stats
        adv.offense_explosiveness,
        adv.offense_stuff_rate,
        adv.offense_line_yards,
        adv.offense_second_level_yards,
        adv.offense_open_field_yards,
        -- Add more columns as needed
        g.season,
        g.week,
        g.season_type,
        g.start_date,
        g.neutral_site,
        g.conference_game,
        g.attendance,
        g.venue_id,
        g.venue,
        g.home_team,
        g.away_team,
        g.home_conference,
        g.away_conference,
        g.home_points,
        g.away_points,
        g.excitement_index,
        -- Add more joins and columns as needed
        CASE 
            WHEN tgs.school = g.home_team THEN g.away_team
            ELSE g.home_team
        END AS opponent,
        CASE 
            WHEN tgs.school = g.home_team THEN g.away_conference
            ELSE g.home_conference
        END AS opponent_conference,
        CASE 
            WHEN tgs.school = g.home_team THEN g.away_points
            ELSE g.home_points
        END AS opponent_points,
        CASE 
            WHEN tgs.school = g.home_team THEN 1
            ELSE 0
        END AS is_home
    FROM team_game_stats tgs
    LEFT JOIN advanced_team_game_stats adv ON tgs.id = adv.game_id AND tgs.school = adv.team
    LEFT JOIN games g ON tgs.id = g.id
    -- Add more LEFT JOINs here for additional tables
    """

    # Execute the query and fetch results
    source_cursor.execute(query)
    results = source_cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in source_cursor.description]

    # Create the table in the target database
    create_table_query = f"CREATE TABLE IF NOT EXISTS transformed_teams ({', '.join(column_names)})"
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