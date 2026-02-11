from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import execute_sql_query


def format_results_for_display(results: List[Any], limit: int = 10) -> str:
    """
    Format SQL results for display in terminal or UI.
    
    Args:
        results: List of result dictionaries from execute_sql_query
        limit: Maximum number of rows to display
        
    Returns:
        Formatted string representation of results
    """
    if not results:
        return "No results found"
    
    lines = [f"Found {len(results)} result(s):"]
    
    for i, row in enumerate(results[:limit], 1):
        lines.append(f"  {i}. {row}")
    
    if len(results) > limit:
        lines.append(f"  ... and {len(results) - limit} more rows")
    
    return "\n".join(lines)


def data_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute SQL query and return results.
    
    Args:
        state: Current agent state with sql_query
        
    Returns:
        Updated state with raw_result and optional error
    """
    print("[DATA AGENT] Executing SQL query...")
    
    sql_query = state.get('sql_query', '')
    
    if not sql_query:
        print("ERROR: No SQL query provided")
        return {"raw_result": None}
    
    print(f"Query: {sql_query[:100]}...")
    
    try:
        # Execute SQL query
        results = execute_sql_query(sql_query)
        
        print("Query executed successfully")
        print(format_results_for_display(results, limit=5))
        print("[DATA AGENT] Complete")
        print()
        
        return {"raw_result": results}
        
    except Exception as e:
        print(f"ERROR: Failed executing query: {e}")
        print("[DATA AGENT] Failed")
        print()
        
        return {
            "raw_result": None,
            "error": str(e)
        }