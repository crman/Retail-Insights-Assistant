from langgraph.graph import StateGraph
from agents.state import AgentState
from agents.query_agent import query_agent
from agents.data_agent import data_agent
from agents.validation_agent import validation_agent


# Create the state graph
builder = StateGraph(AgentState)

# Add nodes for each agent
builder.add_node("query_agent", query_agent)
builder.add_node("data_agent", data_agent)
builder.add_node("validation_agent", validation_agent)

# Define routing logic
def router(state: AgentState):
    """
    Route to data_agent if SQL was generated, 
    otherwise skip to validation if clarification is needed.
    """
    sql = state.get("sql_query", "")
    if sql and "CLARIFICATION_REQUIRED" in sql:
        return "validation_agent"
    return "data_agent"

# Start with query agent
builder.set_entry_point("query_agent")

# Conditional routing from query agent
builder.add_conditional_edges(
    "query_agent",
    router,
    {
        "data_agent": "data_agent",
        "validation_agent": "validation_agent"
    }
)

# Data agent → Validation agent
builder.add_edge("data_agent", "validation_agent")

# End at validation agent
builder.set_finish_point("validation_agent")

# Compile the graph
graph = builder.compile()