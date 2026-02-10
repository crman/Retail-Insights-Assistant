from dotenv import load_dotenv
import os

# Load environment variables FIRST before importing any modules that need them
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Now import graph (which will import agents that need the env vars)
from graph import graph


print("="*60)
print("🚀 Retail Insights Assistant (Multi-Agent System)")
print("="*60)
print("Type 'exit' to quit\n")



while True:
    mode = input("\n📋 Mode (qa/summary/exit): ").lower()
    if mode == "exit":
        print("\n👋 Goodbye!")
        break

    question = ""
    if mode == "qa":
        question = input("❓ Ask your question: ")
    
    print("\n" + "="*60)
    print(f"🔄 STARTING EXECUTION - Mode: {mode.upper()}")
    print("="*60 + "\n")

    result = graph.invoke({
        "mode": mode,
        "question": question
    })

    print("\n" + "="*60)
    print("✅ FINAL ANSWER:")
    print("="*60)
    print(result["final_answer"])
    print("="*60)