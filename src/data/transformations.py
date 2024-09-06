# Data Transformations

import sqlite3
import json
import pandas as pd
import numpy as np

def connect_to_db(db_path):
    return sqlite3.connect(db_path)

def get_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def json_to_dataframe(json_data):
    df = pd.json_normalize(json_data)
    return df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

def transform_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT data FROM {table_name}")
    json_data = [json.loads(row[0]) for row in cursor.fetchall()]
    
    if not json_data:
        print(f"Warning: No data found for table {table_name}")
        return pd.DataFrame()
    
    if table_name == 'team_game_stats':
        return transform_team_game_stats(json_data)
    elif table_name == 'betting_lines':
        return transform_betting_lines(json_data)
    
    df = json_to_dataframe(json_data)
    return df

def transform_team_game_stats(json_data):
    rows = []
    for game in json_data:
        try:
            for team in game['teams']:
                row = {
                    'id': game['id'],
                    'school_id': team.get('school_id', ''),
                    'school': team.get('school', ''),
                    'conference': team.get('conference', ''),
                    'home_away': team.get('home_away', ''),
                    'points': team.get('points', '')
                }
                for stat in team.get('stats', []):
                    row[stat.get('category', '')] = stat.get('stat', '')
                rows.append(row)
        except Exception as e:
            print(f"Error processing game data: {e}")
            print(f"Problematic game data: {game}")
    return pd.DataFrame(rows)

def transform_betting_lines(json_data):
    rows = []
    line_columns = ['provider', 'spread', 'formatted_spread', 'spread_open', 'over_under', 
                    'over_under_open', 'home_moneyline', 'away_moneyline']
    
    for game in json_data:
        base_row = {k: v for k, v in game.items() if k != 'lines'}
        
        # Add null values for all line columns as the base case
        for col in line_columns:
            base_row[f'line_{col}'] = None
        
        if 'lines' in game and isinstance(game['lines'], list) and game['lines']:
            for line in game['lines']:
                row = base_row.copy()
                for col in line_columns:
                    row[f'line_{col}'] = line.get(col, None)
                rows.append(row)
    
    return pd.DataFrame(rows)


def save_to_new_db(df, table_name, new_conn):
    if not isinstance(df, pd.DataFrame):
        print(f"Error: Expected DataFrame for table {table_name}, but got {type(df)}")
        print(f"Data: {df}")
        return
    
    if df.empty:
        print(f"Warning: Empty DataFrame for table {table_name}")
        return
    
    # Replace any characters that might cause SQL syntax errors
    df.columns = [str(col).replace(".", "_").replace("[", "_").replace("]", "_") for col in df.columns]
    
    # Ensure all data is stored as text
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    # Use a try-except block to catch and print any errors
    try:
        df.to_sql(table_name, new_conn, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error saving table {table_name}: {str(e)}")
        print(f"Problematic columns: {df.columns.tolist()}")
        print(f"Sample data: \n{df.head()}")
        raise

def main():
    old_db_path = '../data/01_raw/college_football.db'
    new_db_path = '../data/02_interim/college_football.db'
    
    old_conn = connect_to_db(old_db_path)
    new_conn = connect_to_db(new_db_path)
    
    table_names = get_table_names(old_conn)
    
    for table_name in table_names:
        print(f"Transforming table: {table_name}")
        df = transform_table(old_conn, table_name)
        save_to_new_db(df, table_name, new_conn)
    
    old_conn.close()
    new_conn.close()
    print("Transformation complete.")

if __name__ == "__main__":
    main()