from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import pandas as pd

llm = ChatGroq(model="llama-3.3-70b-versatile")

with open("prompts/summary_prompt.txt") as f:
    template = f.read()

PROMPT = PromptTemplate(
    input_variables=["metrics"],
    template=template
)

product_df = pd.read_csv("data/May-2022.csv")
stock_df = pd.read_csv("data/Sale Report.csv")

def summary_agent(state):
    print("📈 [SUMMARY AGENT] Generating executive summary...")
    print("   📊 Calculating metrics from data...")
    
    # Convert numeric columns to proper types
    product_df["Final MRP Old"] = pd.to_numeric(product_df["Final MRP Old"], errors='coerce')
    product_df["TP"] = pd.to_numeric(product_df["TP"], errors='coerce')
    stock_df["Stock"] = pd.to_numeric(stock_df["Stock"], errors='coerce')
    
    metrics = {
        "total_products": len(product_df),
        "avg_mrp": product_df["Final MRP Old"].mean(),
        "avg_margin": (product_df["Final MRP Old"] - product_df["TP"]).mean(),
        "total_stock": stock_df["Stock"].sum()
    }
    
    print(f"   Metrics: {metrics}")
    print("   🤖 Asking LLM to generate summary...")

    response = llm.invoke(
        PROMPT.format(metrics=metrics)
    ).content
    
    print("   [SUMMARY AGENT] Complete!\n")

    return {"final_answer": response}