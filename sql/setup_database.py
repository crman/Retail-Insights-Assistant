import os
import sqlite3
from typing import Dict, List

import pandas as pd

# Constants - paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(SCRIPT_DIR, "retail_data.db")
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

# Mapping of table names to CSV files
CSV_TO_TABLE_MAPPING: Dict[str, str] = {
    "may_2022_products": "May-2022.csv",
    "sale_report": "Sale Report.csv",
    "amazon_sales": "Amazon Sale Report.csv",
    "international_sales": "International sale Report.csv",
    "pl_march_2021": "P  L March 2021.csv",
    "cloud_warehouse": "Cloud Warehouse Compersion Chart.csv",
    "expense_iigf": "Expense IIGF.csv",
}


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize column names.
    - Strips whitespace
    - Converts hyphens and spaces to underscores
    - Removes special characters
    - Lowercases all column names
    - Renames 'index' to 'row_index' (reserved keyword in SQLite)
    - Renames 'Unnamed_*' columns to 'extra_column_N'
    """
    # Strip leading/trailing whitespace
    df.columns = df.columns.str.strip()
    # Replace hyphens with spaces (so they become underscores in the next step)
    df.columns = df.columns.str.replace('-', ' ', regex=False)
    # Replace whitespace sequences with underscores
    df.columns = df.columns.str.replace(r'\s+', '_', regex=True)
    # Remove remaining special characters (keep letters, digits, underscores)
    df.columns = df.columns.str.replace(r'[^\w]', '', regex=True)
    # Lowercase for consistency
    df.columns = df.columns.str.lower()

    # Rename artifact columns instead of dropping them
    renamed = {}
    extra_col_counter = 1
    new_columns = []
    for col in df.columns:
        if col == 'index':
            renamed[col] = 'row_index'
            new_columns.append('row_index')
        elif col.startswith('unnamed'):
            new_name = f'extra_column_{extra_col_counter}'
            renamed[col] = new_name
            new_columns.append(new_name)
            extra_col_counter += 1
        else:
            new_columns.append(col)

    if renamed:
        print(f"  Renamed columns: {renamed}")
    df.columns = new_columns

    return df


def get_table_info(conn: sqlite3.Connection, table_name: str) -> Dict:
    """
    Get information about a table
    """
    cursor = conn.cursor()
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    return {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": len(columns),
        "columns": [(col[1], col[2]) for col in columns]  # (name, type)
    }


def setup_database() -> None:
    """
    Main function to set up the SQLite3 database from CSV files
    """
    print("=" * 70)
    print("Retail Insights Database Setup")
    print("=" * 70)
    print()
    
    # Remove existing database if it exists
    if os.path.exists(DATABASE_PATH):
        print(f"WARNING: Removing existing database: {DATABASE_PATH}")
        os.remove(DATABASE_PATH)
    
    # Create SQLite3 connection
    print(f"Creating new database: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    
    tables_created: List[str] = []
    tables_info: List[Dict] = []
    
    # Process each CSV file
    for table_name, csv_file in CSV_TO_TABLE_MAPPING.items():
        csv_path = os.path.join(DATA_DIR, csv_file)
        
        if not os.path.exists(csv_path):
            print(f"WARNING: Skipping {csv_file} - File not found")
            continue
        
        try:
            print(f"\nProcessing: {csv_file}")
            print(f"Table name: {table_name}")
            
            # Read CSV
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Clean column names
            df = clean_column_names(df)
            
            # Create table in SQLite3 using pandas (don't create index to avoid duplicates)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Get table info
            info = get_table_info(conn, table_name)
            tables_info.append(info)
            tables_created.append(table_name)
            
            print(f"SUCCESS: Created table with {info['row_count']} rows")
            
        except Exception as e:
            print(f"ERROR: Failed processing {csv_file}: {e}")
            continue
    
    # Print summary
    print("\n" + "=" * 70)
    print("Database Summary")
    print("=" * 70)
    print(f"Total tables created: {len(tables_created)}")
    print()
    
    for info in tables_info:
        print(f"Table: {info['table_name']}")
        print(f"Rows: {info['row_count']:,}")
        print(f"Columns: {info['column_count']}")
        print(f"Sample columns: {', '.join([col[0] for col in info['columns'][:5]])}")
        print()
    
    # Close connection
    conn.close()
    
    print("=" * 70)
    print("Database setup complete!")
    print("=" * 70)


if __name__ == "__main__":
    setup_database()
