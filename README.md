# Retail Insights Assistant 🚀

A **GenAI-powered multi-agent system** for analyzing retail sales data using natural language queries. Built with LangGraph, SQLite3, and Groq/Gemini LLMs.

## 📋 Features

- **Text-to-SQL** conversion using curated prompt engineering.
- **Multi-agent architecture**:
  - **Query Agent**: Logic for translating natural language to SQLite.
  - **Data Agent**: Robust execution and error handling.
  - **Validation Agent**: Business insight generation and response verification.
- **Two modes**: QA (specific questions) and Summary (dataset overview).
- **SQLite3** data layer for efficient local analysis.
- **Natural language** answers with professional business insights.

## 🏗️ Architecture

```
User Input → Query Agent → Data Agent → Validation Agent → Natural Language Answer
              (Text→SQL)    (Execute)     (Verify & Summarize)
```

## 🚀 Execution Guide

Follow these steps to set up and run the assistant on your local machine.

### 1. Prerequisite: Python Environment

Ensure you have Python 3.10 or higher installed.

```bash
# Clone the repository (if applicable)
# cd Retail-Insights-Assistant

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory and add your API keys. The application supports Groq (default) and Google Gemini.

```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Initialize Database

Before running the app, you need to convert the raw CSV data into a SQLite database. This script handles data cleaning and schema creation.

```bash
python sql/setup_database.py
```

### 5. Run the Application

Start the conversational assistant:

```bash
python app.py
```

## 📊 Usage

Once the application is running:

1. **Select a table** from the detected CSVs.
2. **Choose a mode**:
   - **QA Mode**: Ask specific questions like *"Which product line had the highest sales in Q3?"*
   - **Summary Mode**: Get an automated business overview of the entire table.

## 📁 Project Structure

```
Retail-Insights-Assistant/
├── agents/
│   ├── query_agent.py      # Text-to-SQL generation
│   ├── data_agent.py       # SQL execution & formatting
│   ├── validation_agent.py # Insight verification & summary
│   └── state.py            # LangGraph state definition
├── configs/
│   ├── config.py           # App & LLM configurations
│   └── env_config.py       # Environment variable loader
├── prompts/
│   ├── qa_sql_prompt.txt      # Prompt for QA mode
│   ├── summary_sql_prompt.txt # Prompt for Summary mode
│   └── validation_prompt.txt  # Human-readable insight prompt
├── sql/
│   ├── setup_database.py   # Data ingestion & cleaning script
│   └── retail_data.db      # Generated SQLite database
├── utils/
│   └── db_utils.py          # Database helper functions
├── data/                    # Raw CSV datasets
├── graph.py                 # LangGraph workflow definition
├── app.py                   # Main entry point (Streamlit/CLI)
└── requirements.txt
```

## 🛠️ Technologies

- **LangGraph**: Multi-agent orchestration and state management.
- **SQLite3**: Local relational database for structured querying.
- **Groq**: Ultra-fast LLM inference (Llama 3 / Mixtral).
- **Google Gemini**: Alternative LLM provider support.
- **Pandas**: Data cleaning and preprocessing during ingestion.

