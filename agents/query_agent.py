import json
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS



llm = ChatGroq(model="llama-3.3-70b-versatile")
db = FAISS.load_local(
    "vector_store/vector_store/index", 
    GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
    allow_dangerous_deserialization=True  # We trust this file as we created it
)

with open("prompts/query_generation_prompt.txt") as f:
    template = f.read()

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)

def query_agent(state):
    print("🔍 [QUERY AGENT] Starting query analysis...")
    print(f"   Question: '{state['question']}'")
    
    # Skip vector search if no question (summary mode)
    if not state["question"] or state["question"].strip() == "":
        print("   ⏭️  No question provided (summary mode), skipping vector search")
        print("   [QUERY AGENT] Complete!\n")
        return {
            "retrieved_context": "",
            "structured_query": {}
        }
    
    # Retrieve relevant files and metadata
    docs = db.similarity_search(state["question"], k=3)
    print(f"\n   📚 Retrieved {len(docs)} relevant documents from vector store:")
    for i, doc in enumerate(docs, 1):
        print(f"      {i}. {doc.page_content[:80]}...")
        if doc.metadata.get("file"):
            print(f"         → File: {doc.metadata['file']}")
    
    # Extract file paths from metadata
    relevant_files = [doc.metadata.get("file") for doc in docs if doc.metadata.get("file")]
    print(f"\n   📁 Selected files: {relevant_files if relevant_files else 'None (using defaults)'}")
    
    # Build context
    context = "\n".join([d.page_content for d in docs])
    
    # Generate structured query with file information
    print("   🤖 Generating structured query with LLM...")
    response = llm.invoke(
        PROMPT.format(
            context=context,
            question=state["question"]
        )
    ).content
    
    print(f"   📝 Raw LLM Response: {response[:200]}...")  # Show first 200 chars
    
    try:
        query = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Parse Error: {e}")
        print(f"   Full response: {response}")
        # Fallback to a default query
        query = {
            "metric": "count",
            "filters": {}
        }
        print(f"   ⚠️  Using fallback query: {query}")
    
    query["files"] = relevant_files  # Add file selection to query
    
    print(f"   ✅ Structured Query: {query}")
    print("   [QUERY AGENT] Complete!\n")
    
    return {
        "retrieved_context": context,
        "structured_query": query
    }