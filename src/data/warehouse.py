# Data Warehouse

import sqlite3
import pandas as pd
import json

DB_FILE = '../data/01_raw/college_football.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def store_raw_data(data, table_name, if_exists='append', year=None):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone() is not None
        
        # Convert data to JSON strings
        json_data = [json.dumps(item) for item in data]
        
        if not table_exists:
            cursor.execute(f"CREATE TABLE {table_name} (year INTEGER, data JSON)")
            print(f"Created table {table_name}")
        
        # Determine the year field based on the table_name
        year_field = 'season' if table_name in ['betting_lines', 'games', 'pregame_win_probabilities'] else 'year'
        
        if year is not None:
            # Delete existing data for the specific year
            cursor.execute(f"DELETE FROM {table_name} WHERE json_extract(data, '$.{year_field}') = ?", (year,))
            # Insert new data for the year
            cursor.executemany(f"INSERT INTO {table_name} (year, data) VALUES (?, ?)", [(year, item) for item in json_data])
            print(f"Updated data for year {year} in {table_name}")
        else:
            # Append all data if no specific year is provided
            cursor.executemany(f"INSERT INTO {table_name} (year, data) VALUES (?, ?)", 
                               [(json.loads(item)[year_field], item) for item in json_data])
            print(f"Appended data in {table_name}")
        
        conn.commit()
        conn.close()
    else:
        print("Error! Cannot create the database connection.")


def store_team_game_stats(data, table_name):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone() is not None
        
        # If the table does not exist, create it with 'id' as primary key
        if not table_exists:
            cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, data JSON)")
            print(f"Created table {table_name}")
        
        # Prepare data for insertion
        insert_data = []
        for item in data:
            id = item['id']
            data_json = json.dumps(item)
            insert_data.append((id, data_json))
        
        # Use 'INSERT OR REPLACE INTO' to update existing records and insert new ones
        cursor.executemany(f"INSERT OR REPLACE INTO {table_name} (id, data) VALUES (?, ?)", insert_data)
        print(f"Inserted/Updated data in {table_name}")
        
        conn.commit()
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def fetch_raw_data(table_name):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(f"SELECT data FROM {table_name}")
        raw_data = cursor.fetchall()
        conn.close()
        return [json.loads(item[0]) for item in raw_data]
    else:
        print("Error! Cannot create the database connection.")
        return None

def get_last_update(table_name):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone() is None:
            print(f"Table '{table_name}' does not exist yet.")
            conn.close()
            return None
        
        cursor.execute(f"SELECT MAX(json_extract(data, '$.season')) as last_season FROM {table_name}")
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] is not None else None
    else:
        print("Error! Cannot create the database connection.")
        return None

def store_calendar_data(data, year):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            cursor.execute("CREATE TABLE calendar (year INTEGER, data JSON)")
            print("Created table calendar")
        
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Insert or replace data for the given year
        cursor.execute("INSERT OR REPLACE INTO calendar (year, data) VALUES (?, ?)", (year, json_data))
        
        conn.commit()
        conn.close()
        print(f"Calendar data for year {year} stored/updated")
    else:
        print("Error! Cannot create the database connection.")

def fetch_calendar_data(year):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("Calendar table does not exist yet.")
            conn.close()
            return None
        
        cursor.execute("SELECT data FROM calendar WHERE year = ?", (year,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        else:
            print(f"No calendar data found for year {year}")
            return None
    else:
        print("Error! Cannot create the database connection.")
        return None
    
def store_advanced_team_game_stats(data, table_name):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone() is not None
        
        # If the table does not exist, create it with a composite primary key
        if not table_exists:
            cursor.execute(f"""
                CREATE TABLE {table_name} (
                    game_id INTEGER,
                    team TEXT,
                    data JSON,
                    PRIMARY KEY (game_id, team)
                )
            """)
            print(f"Created table {table_name}")
        
        # Prepare data for insertion
        insert_data = []
        for item in data:
            game_id = item['game_id']
            team = item['team']
            data_json = json.dumps(item)
            insert_data.append((game_id, team, data_json))
        
        # Use 'INSERT OR REPLACE INTO' to update existing records and insert new ones
        cursor.executemany(
            f"INSERT OR REPLACE INTO {table_name} (game_id, team, data) VALUES (?, ?, ?)",
            insert_data
        )
        print(f"Inserted/Updated data in {table_name}")
        
        conn.commit()
        conn.close()
    else:
        print("Error! Cannot create the database connection.")


def drop_table(db_file, table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # SQL command to drop the table
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"

        # Execute the DROP TABLE command
        cursor.execute(drop_table_sql)
        print(f"Table '{table_name}' has been dropped successfully.")
        
        # Commit the changes
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()