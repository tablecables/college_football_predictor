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

def store_raw_data(data, table_name, if_exists='append'):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone() is not None
        
        # Convert data to JSON strings
        json_data = [json.dumps(item) for item in data]
        
        if not table_exists or if_exists == 'replace':
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(f"CREATE TABLE {table_name} (data JSON)")
            print(f"{'Created' if not table_exists else 'Replaced'} table {table_name}")
        
        # Insert data
        cursor.executemany(f"INSERT INTO {table_name} (data) VALUES (?)", [(item,) for item in json_data])
        
        conn.commit()
        conn.close()
        print(f"Data {'replaced' if if_exists == 'replace' else 'appended'} in {table_name}")
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