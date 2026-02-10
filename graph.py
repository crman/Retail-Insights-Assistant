from langgraph.graph import StateGraph
from agents.state import AgentState
from agents.query_agent import query_agent
from agents.data_agent import data_agent
from agents.validation_agent import validation_agent
from agents.summary_agent import summary_agent

builder = StateGraph(AgentState)

builder.add_node("query_agent", query_agent)
builder.add_node("data_agent", data_agent)
builder.add_node("validation_agent", validation_agent)
builder.add_node("summary_agent", summary_agent)

builder.set_entry_point("query_agent")

def route(state):
    next_agent = "summary_agent" if state["mode"] == "summary" else "data_agent"
    print(f"🔀 [ROUTER] Mode='{state['mode']}' → Routing to: {next_agent.upper()}\n")
    return next_agent

builder.add_conditional_edges("query_agent", route)
builder.add_edge("data_agent", "validation_agent")
builder.set_finish_point("validation_agent")
builder.set_finish_point("summary_agent")

graph = builder.compile()