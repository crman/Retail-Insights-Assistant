import streamlit as st
from graph import graph
from utils.db_utils import get_available_tables, get_table_preview

# Set up the page
st.set_page_config(
    page_title="Retail Insights Assistant",
    page_icon="🚀",
    layout="wide"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Hello! I'm your Retail Insights Assistant.**\n\nI can help you analyze your sales data, find trends, or summarize entire datasets. How can I assist you today?"}
    ]
if "last_table" not in st.session_state:
    st.session_state.last_table = None


def clear_history(is_manual=False):
    st.session_state.history = []

    if is_manual:
        msg = "👋 **History cleared.** How else can I help you analyze your data?"
    else:
        msg = "👋 **Hello! I'm your Retail Insights Assistant.**\n\nI can help you analyze your sales data, find trends, or summarize entire datasets. How can I assist you today?"

    st.session_state.messages = [{"role": "assistant", "content": msg}]


# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Select table
    try:
        tables = get_available_tables()
        if not tables:
            st.error("No tables found. Please run 'python sql/setup_database.py'.")
            st.stop()
            
        selected_table = st.selectbox(
            "Select Data Table",
            options=tables,
            index=0,
            on_change=clear_history
        )
        
        # Show table preview in sidebar
        st.info(get_table_preview(selected_table))
        
    except Exception as e:
        st.error(f"Error loading tables: {e}")
        st.stop()

    st.divider()
    
    # Select mode
    mode = st.radio(
        "Operation Mode",
        options=["QA Mode", "Summary Mode"],
        on_change=clear_history
    )
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        clear_history(is_manual=True)
        st.rerun()

# Main UI
st.title("🛒 Retail Insights Assistant")
st.markdown(f"**Currently analyzing:** `{selected_table}` | **Mode:** `{mode}`")

if mode == "Summary Mode":
    st.subheader("📊 Dataset Summary")
    st.write("Generate a comprehensive overview of the selected dataset.")
    
    if st.button("Generate Summary"):
        with st.spinner("Analyzing data and generating insights..."):
            try:
                result = graph.invoke({
                    "mode": "summary",
                    "table": selected_table,
                    "question": "",
                    "table_schema": None,
                    "sql_query": None,
                    "raw_result": None,
                    "final_answer": None,
                    "history": [] # Summary doesn't usually use history
                })
                
                st.success("Summary Generated!")
                st.markdown("### Executive Summary")
                st.markdown(result["final_answer"])

                # Optionally show the SQL used
                with st.expander("View SQL Analysis"):
                    st.code(result["sql_query"], language="sql")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

else: # QA Mode
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = graph.invoke({
                        "mode": "qa",
                        "table": selected_table,
                        "question": prompt,
                        "table_schema": None,
                        "sql_query": None,
                        "raw_result": None,
                        "final_answer": None,
                        "history": st.session_state.history
                    })
                    
                    full_response = result["final_answer"]
                    st.markdown(full_response)
                    
                    # Store in session state
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Update conversation history for LLM
                    st.session_state.history.append({
                        "question": prompt,
                        "answer": full_response
                    })
                    
                    # Show SQL in expander
                    with st.expander("🔍 View Query Logic"):
                        st.code(result["sql_query"], language="sql")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()
st.caption("Retail Insights Assistant powered by LangGraph, LangChain, SQLite3, and Groq.")
