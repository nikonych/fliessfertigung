import sqlite3
import pandas as pd

def get_db_connection():
    return sqlite3.connect("manufacturing.db")

def fetch_table_data(table_name):
    conn = get_db_connection()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df