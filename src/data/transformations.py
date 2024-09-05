# Data Transformations

import sqlite3
import json
import pandas as pd

def connect_to_db(db_path):
    return sqlite3.connect(db_path)

def get_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def json_to_dataframe(json_data):
    return pd.json_normalize(json_data)

def transform_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT data FROM {table_name}")
    json_data = [json.loads(row[0]) for row in cursor.fetchall()]
    df = json_to_dataframe(json_data)
    return df

def save_to_new_db(df, table_name, new_conn):
    df.to_sql(table_name, new_conn, if_exists='replace', index=False)

def main():
    old_db_path = '../data/01_raw/college_football.db'
    new_db_path = '../data/02_interim/college_football_tabular.db'
    
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