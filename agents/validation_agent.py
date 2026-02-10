from langchain_groq import ChatGroq 
from langchain_core.prompts import PromptTemplate
import os

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

llm = ChatGroq(model="llama-3.3-70b-versatile")

with open("prompts/validation_prompt.txt") as f:
    template = f.read()

PROMPT = PromptTemplate(
    input_variables=["query", "result"],
    template=template
)

def validation_agent(state):
    print("✅ [VALIDATION AGENT] Generating business explanation...")
    print(f"   Raw result: {state['raw_result']}")
    print("   🤖 Asking LLM to explain in business terms...")
    
    explanation = llm.invoke(
        PROMPT.format(
            query=state["structured_query"],
            result=state["raw_result"]
        )
    ).content
    
    print("   [VALIDATION AGENT] Complete!\n")
    return {"final_answer": explanation}