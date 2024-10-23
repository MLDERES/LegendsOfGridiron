import sqlite3
from pathlib import Path
import pandas as pd

DATA_PATH = Path('data')

# Run a sqlite query
def run_query(q, cols=None):
    conn = sqlite3.connect(DATA_PATH/'league_db.db')
    rows = conn.execute(q).fetchall()
    if cols is None:
        cols = [desc[0] for desc in conn.execute(q).description]
    df = pd.DataFrame(rows, columns=cols)
    return df

def run_query_scalar(q):
    conn = sqlite3.connect(DATA_PATH/'league_db.db')
    rows = conn.execute(q).fetchone()
    return rows[0]

def get_column_names(table_name):
    # Connect to the SQLite3 database
    conn = sqlite3.connect(DATA_PATH/'league_db.db')
    cursor = conn.cursor()
    
    # Execute PRAGMA table_info to get the column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    
    # Fetch all results
    columns_info = cursor.fetchall()
    
    # Extract column names
    column_names = [info[1] for info in columns_info]
    
    # Close the connection
    conn.close()
    
    return column_names

def table_names():
    # Get the list of tables in teh sqlite database
    conn = sqlite3.connect(DATA_PATH/'league_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables


for table in table_names():
    print(f'{table[0]}: {get_column_names(table[0])}')
    