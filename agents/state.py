from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict):
    """
    Shared state for all agents in the multi-agent system.
    
    Attributes:
        mode: Operation mode - 'qa' for questions, 'summary' for summaries
        table: Selected database table name
        question: User's natural language question (empty for summary mode)
        table_schema: Schema information for the selected table
        sql_query: Generated SQL query
        raw_result: Raw results from SQL execution
        final_answer: Natural language answer for the user
    """
    mode: str
    table: str
    question: str
    table_schema: Optional[Dict[str, Any]]
    sql_query: Optional[str]
    raw_result: Optional[List[Any]]
    final_answer: Optional[str]