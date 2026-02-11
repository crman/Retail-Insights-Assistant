from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from configs import config
from utils.db_utils import get_table_schema


# Initialize LLM
llm = ChatGroq(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)


def load_prompt_template(mode: str) -> PromptTemplate:
    """
    Load the appropriate prompt template based on mode.
    
    Args:
        mode: The operation mode ('qa' or 'summary')
        
    Returns:
        PromptTemplate object
    """
    prompt_file = f"prompts/{mode}_sql_prompt.txt"
    try:
        with open(prompt_file, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"ERROR: Prompt file {prompt_file} not found.")
        template = "Question: {question}\nSQL Query:"

    if mode == "qa":
        return PromptTemplate(
            input_variables=["table_name", "schema", "question", "history"],
            template=template
        )
    else:  # summary
        return PromptTemplate(
            input_variables=["table_name", "schema"],
            template=template
        )


def format_history_for_prompt(history: List[Dict[str, str]]) -> str:
    """
    Format previous conversation turns for LLM prompt.
    
    Args:
        history: List of previous conversation turns
        
    Returns:
        Formatted string of the conversation history
    """
    if not history:
        return "No previous interactions."
    
    formatted_turns = []
    # Only take last 5 turns to avoid context overflow
    for turn in history[-5:]:
        formatted_turns.append(f"Q: {turn['question']}\nA: {turn['answer']}")
        
    return "\n\n".join(formatted_turns)


def format_schema_for_prompt(schema: Dict[str, Any]) -> str:
    """
    Format schema information for LLM prompt.
    
    Args:
        schema: Dictionary containing table name and column info
        
    Returns:
        Formatted string of the table schema
    """
    lines = [
        f"Table: {schema['table_name']}",
        f"Total Rows: {schema.get('row_count', 0):,}",
        "\nColumns:",
    ]
    
    for col in schema.get('columns', []):
        # Handle both dict format (SQLite3) and tuple format (legacy)
        if isinstance(col, dict):
            col_name = col.get('name', 'unknown')
            col_type = col.get('type', 'unknown')
        else:
            col_name, col_type = col
        lines.append(f"  - {col_name} ({col_type})")
    
    return "\n".join(lines)


def query_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate SQL query from natural language question or summary request.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with updated table_schema and sql_query
    """
    print("[QUERY AGENT] Starting SQL query generation...")
    print(f"Mode: {state.get('mode', 'QA').upper()}")
    print(f"Table: {state.get('table', 'unknown')}")
    
    if state.get('mode') == 'qa':
        print(f"Question: '{state.get('question', '')}'")
    
    try:
        # Get table schema
        print("Retrieving table schema...")
        schema = get_table_schema(state['table'])
        print(f"Found {len(schema['columns'])} columns, {schema['row_count']:,} rows")
        
        # Format schema for prompt
        schema_text = format_schema_for_prompt(schema)
        
        # Load appropriate prompt template
        prompt_template = load_prompt_template(state['mode'])
        
        # Format prompt
        if state['mode'] == 'qa':
            history_text = format_history_for_prompt(state.get('history', []))
            prompt_text = prompt_template.format(
                table_name=state['table'],
                schema=schema_text,
                question=state['question'],
                history=history_text
            )
        else:  # summary
            prompt_text = prompt_template.format(
                table_name=state['table'],
                schema=schema_text
            )
            
        print("Generating SQL query with LLM...")
        response = llm.invoke(prompt_text).content.strip()
        
        # Check for clarification request
        if "CLARIFICATION_REQUIRED" in response:
            print("  Result: Clarification requested by LLM")
            return {
                "sql_query": response,
                "table_schema": schema
            }

        # Extract SQL query (remove markdown formatting)
        sql_query = response
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].split("```")[0].strip()
        
        print(f"Generated SQL Query:\n{sql_query}")
        print("[QUERY AGENT] Complete\n")
        
        return {
            "table_schema": schema,
            "sql_query": sql_query
        }
    except Exception as e:
        print(f"ERROR: Query generation failed: {e}")
        return {
            "sql_query": None,
            "error": str(e)
        }