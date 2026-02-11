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
    """
    prompt_file = f"prompts/{mode}_sql_prompt.txt"
    
    with open(prompt_file, 'r') as f:
        template = f.read()
    
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
    """
    lines = [
        f"Table: {schema['table_name']}",
        f"Total Rows: {schema['row_count']:,}",
        "\nColumns:",
    ]
    
    for col in schema['columns']:
        # Handle both dict format (SQLite3) and tuple format (legacy)
        if isinstance(col, dict):
            col_name = col['name']
            col_type = col['type']
        else:
            col_name, col_type = col
        lines.append(f"  - {col_name} ({col_type})")
    
    return "\n".join(lines)


def query_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate SQL query from natural language question or summary request.
    """
    print("[QUERY AGENT] Starting SQL query generation...")
    print(f"Mode: {state['mode'].upper()}")
    print(f"Table: {state['table']}")
    
    if state['mode'] == 'qa':
        print(f"Question: '{state['question']}'")
    
    # Get table schema
    print("Retrieving table schema...")
    schema = get_table_schema(state['table'])
    print(f"Found {len(schema['columns'])} columns, {schema['row_count']:,} rows")
    
    # Format schema for prompt
    schema_text = format_schema_for_prompt(schema)
    
    # Load appropriate prompt template
    prompt_template = load_prompt_template(state['mode'])
    
    # Generate SQL query
    print("Generating SQL query with LLM...")
    
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
    
    response = llm.invoke(prompt_text).content.strip()
    
    # Check for clarification request
    if "CLARIFICATION_REQUIRED" in response:
        print("  Result: Clarification requested by LLM")
        return {
            "sql_query": response, # Pass the message directly
            "table_schema": schema
        }

    # Extract SQL query (remove markdown formatting if present)
    sql_query = response
    if sql_query.startswith("```sql"):
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    elif sql_query.startswith("```"):
        sql_query = sql_query.replace("```", "").strip()
    
    print("Generated SQL Query:")
    print(sql_query)
    print("[QUERY AGENT] Complete")
    print()
    
    return {
        "table_schema": schema,
        "sql_query": sql_query
    }