"""
Database utility functions for SQLite3 operations.
"""

import sqlite3
from typing import Any, Dict, List

from configs import config


# Database configuration
DATABASE_PATH = config.DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        SQLite3 connection object
    """
    return sqlite3.connect(DATABASE_PATH)


def get_available_tables() -> List[str]:
    """
    Get list of all tables in the database.
    
    Returns:
        List of table names
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return tables


def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get schema information for a specific table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Dictionary containing table schema information
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    conn.close()
    
    columns = [
        {
            "name": col[1],
            "type": col[2],
            "notnull": bool(col[3]),
            "default": col[4],
            "pk": bool(col[5])
        }
        for col in columns_info
    ]
    
    return {
        "table_name": table_name,
        "columns": columns,
        "row_count": row_count
    }


def get_table_preview(table_name: str) -> str:
    """
    Get a preview string for a table (for display purposes).
    
    Args:
        table_name: Name of the table
        
    Returns:
        String with table preview info
    """
    try:
        schema = get_table_schema(table_name)
        row_count = schema['row_count']
        columns = schema['columns']
        
        # Get first few column names
        col_names = [col['name'] for col in columns[:5]]
        col_preview = ', '.join(col_names)
        
        if len(columns) > 5:
            col_preview += ', ...'
        
        return f"Table: {table_name}\n   Rows: {row_count:,}\n   Columns: {len(columns)}\n   Sample columns: {col_preview}"
    except Exception as e:
        return f"Error loading preview: {e}"


def execute_sql_query(sql_query: str) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results.
    
    Args:
        sql_query: SQL query string
        
    Returns:
        List of dictionaries, each representing a row
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql_query)
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    # Fetch all rows
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    results = [
        dict(zip(column_names, row))
        for row in rows
    ]
    
    return results


def format_results_for_display(results: List[Dict[str, Any]], limit: int = 10) -> str:
    """
    Format query results for display.
    
    Args:
        results: List of result dictionaries
        limit: Maximum number of rows to display
        
    Returns:
        Formatted string representation
    """
    if not results:
        return "No results found"
    
    display_results = results[:limit]
    
    # Get column names
    columns = list(display_results[0].keys())
    
    # Create formatted output
    output_lines = [f"Found {len(results)} result(s):"]
    
    for i, row in enumerate(display_results, 1):
        row_str = ", ".join([f"{k}={v}" for k, v in row.items()])
        output_lines.append(f"  Row {i}: {row_str}")
    
    if len(results) > limit:
        output_lines.append(f"  ... and {len(results) - limit} more rows")
    
    return "\n".join(output_lines)


def format_results_for_llm(results: List[Dict[str, Any]]) -> str:
    """
    Format query results for LLM consumption.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Formatted string for LLM
    """
    if not results:
        return "No results found"
    
    # Convert to a simple table format
    output_lines = []
    
    # Header
    columns = list(results[0].keys())
    output_lines.append(" | ".join(columns))
    output_lines.append("-" * 50)
    
    # Rows
    for row in results:
        row_values = [str(row.get(col, "")) for col in columns]
        output_lines.append(" | ".join(row_values))
    
    return "\n".join(output_lines)
