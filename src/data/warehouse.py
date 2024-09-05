# Data Warehouse

import sqlite3
import pandas as pd
import json

DB_FILE = '../data/00_db/college_football.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def store_raw_data(df, table_name, if_exists='append'):
    conn = create_connection()
    if conn is not None:
        # Convert list columns to JSON strings
        for column in df.columns:
            if df[column].apply(lambda x: isinstance(x, list)).any():
                df[column] = df[column].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

        # Store the data
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        
        if if_exists == 'replace':
            print(f"Data for {table_name} has been replaced")
        else:
            print(f"New data appended to {table_name}")

        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def fetch_raw_data(table_name):
    conn = create_connection()
    if conn is not None:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
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
        
        query = f"SELECT MAX(season) as last_season FROM {table_name}"
        try:
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            last_season = df['last_season'].iloc[0]
            
            return last_season
        except pd.io.sql.DatabaseError as e:
            print(f"Error querying table '{table_name}': {e}")
            conn.close()
            return None
    else:
        print("Error! Cannot create the database connection.")
        return None