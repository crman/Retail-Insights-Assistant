from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
import os

# Load environment variables FIRST before importing any modules that need them
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

documents = [
    # File: May-2022.csv
    Document(
        page_content="May-2022.csv contains product catalog with Category, Sku, Final MRP Old, TP for May 2022",
        metadata={"file": "data/May-2022.csv", "type": "product_catalog", "period": "2022-05"}
    ),
    
    # File: Sale Report.csv
    Document(
        page_content="Sale Report.csv contains inventory stock levels per SKU",
        metadata={"file": "data/Sale Report.csv", "type": "inventory", "period": "current"}
    ),
    
    # File: Amazon Sale Report.csv
    Document(
        page_content="Amazon Sale Report.csv contains detailed sales transactions, orders, and fulfillment data",
        metadata={"file": "data/Amazon Sale Report.csv", "type": "sales_transactions", "period": "historical"}
    ),
    
    # File: International sale Report.csv
    Document(
        page_content="International sale Report.csv contains cross-border sales and international market data",
        metadata={"file": "data/International sale Report.csv", "type": "international_sales", "period": "historical"}
    ),
    
    # File: P  L March 2021.csv
    Document(
        page_content="P  L March 2021.csv contains profit and loss statement for March 2021",
        metadata={"file": "data/P  L March 2021.csv", "type": "financial", "period": "2021-03"}
    ),
    
    # Schema and calculation hints
    Document(
        page_content="avg_mrp means average Final MRP Old across products",
        metadata={"type": "calculation_hint"}
    ),
    
    Document(
        page_content="margin is calculated as Final MRP Old minus TP (Trade Price)",
        metadata={"type": "calculation_hint"}
    ),
]
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
db = FAISS.from_documents(documents, embeddings)
db.save_local("vector_store/index")