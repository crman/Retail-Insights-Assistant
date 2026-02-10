from typing import TypedDict, Dict, Any

class AgentState(TypedDict):
    mode: str                # "qa" or "summary"
    question: str
    retrieved_context: str
    structured_query: Dict
    raw_result: Any
    final_answer: str