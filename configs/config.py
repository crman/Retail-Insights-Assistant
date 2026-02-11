"""
Simple Configuration
Loads environment variables and basic app settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set in environment for libraries that need them
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# App Settings
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql", "retail_data.db")
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.3
