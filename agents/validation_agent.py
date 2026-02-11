from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from configs import config


# Initialize LLM
llm = ChatGroq(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)


def load_validation_prompt() -> PromptTemplate:
    """
    Load the validation prompt template.
    """
    with open("prompts/validation_prompt.txt", 'r') as f:
        template = f.read()
    
    return PromptTemplate(
        input_variables=["mode", "question", "sql_query", "results"],
        template=template
    )


def format_results_for_llm(results: list, max_rows: int = 50) -> str:
    """
    Format SQL results for LLM processing.
    """
    if not results:
        return "No results returned from the query."
    
    # Check if it's a single value result (like COUNT, SUM, AVG)
    if len(results) == 1 and len(results[0]) == 1:
        # Get the single value from the dictionary
        value = list(results[0].values())[0]
        key = list(results[0].keys())[0]
        return f"{key}: {value}"
    
    # Multiple rows/columns
    lines = []
    for i, row in enumerate(results[:max_rows], 1):
        row_str = ", ".join([f"{k}={v}" for k, v in row.items()])
        lines.append(f"Row {i}: {row_str}")
    
    if len(results) > max_rows:
        lines.append(f"... and {len(results) - max_rows} more rows")
    
    return "\n".join(lines)


def validation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate SQL results and convert to natural language answer.
    """
    print("[VALIDATION AGENT] Starting result verification and insight generation...")
    
    # Check for execution errors from the data_agent
    if state.get('error'):
        print(f"  Result: Failure (Database Error: {state['error']})")
        return {
            "final_answer": f"I'm sorry, I encountered a technical error while querying the data: {state['error']}. Please try rephrasing your question."
        }
    
    raw_result = state.get('raw_result')
    sql_query = state.get('sql_query', '')
    
    if raw_result is None:
        print("  Result: Empty (No data returned)")
        # We still send it to the LLM to get a "polite" business explanation for empty results
        raw_result = []
    else:
        print(f"  Result: Success ({len(raw_result)} rows found)")
    
    print("  Action: Validating logic and generating executive summary...")
    
    # Format results for LLM
    results_text = format_results_for_llm(raw_result)
    
    # Load prompt template
    prompt_template = load_validation_prompt()
    
    # Generate natural language explanation
    prompt_text = prompt_template.format(
        mode=state.get('mode', 'qa'),
        question=state.get('question', 'summary'),
        sql_query=sql_query,
        results=results_text
    )
    
    try:
        # The LLM now acts as a "Senior Validator" based on the updated prompt
        explanation = llm.invoke(prompt_text).content
        print("  Status: Insight generated successfully.")
    except Exception as e:
        print(f"  ERROR: LLM invocation failed: {type(e).__name__}")
        if not raw_result:
            explanation = "I couldn't find any data matching your request."
        else:
            explanation = f"I found the relevant data, but I'm having trouble summarizing it. Raw results: {results_text[:100]}..."
    
    print("[VALIDATION AGENT] Complete")
    print("-" * 30)
    
    return {"final_answer": explanation}