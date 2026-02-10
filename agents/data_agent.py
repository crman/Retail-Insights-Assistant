import pandas as pd
import os

product_df = pd.read_csv("data/May-2022.csv")
stock_df = pd.read_csv("data/Sale Report.csv")

def data_agent(state):
    print("📊 [DATA AGENT] Loading and processing data...")
    query = state["structured_query"]
    files = query.get("files", ["data/May-2022.csv"])  # Default fallback
    
    print(f"   Query: {query}")
    print(f"   Requested files: {files}")
    
    # Load the relevant CSV(s)
    dataframes = []
    for file_path in files:
        if file_path and os.path.exists(file_path):
            print(f"   📁 Loading: {file_path}")
            df = pd.read_csv(file_path)
            print(f"      → Loaded {len(df)} rows, {len(df.columns)} columns")
            dataframes.append(df)
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    # Combine or select primary dataframe
    if dataframes:
        df = dataframes[0]  # or pd.concat(dataframes) if merging makes sense
        print(f"   ✅ Using dataframe with {len(df)} rows")
    else:
        print("   ⚠️  No files loaded, using default: data/May-2022.csv")
        df = pd.read_csv("data/May-2022.csv")  # Fallback
    
    # Rest of your filtering and calculation logic...
    metric = query["metric"]
    filters = query.get("filters", {})
    
    print(f"\n   🔧 Applying filters: {filters if filters else 'None'}")

    # Apply category filter (skip if category is 'all' or empty)
    if "category" in filters and filters["category"]:
        # Skip if the filter is ['all'] or similar
        if filters["category"] != ["all"] and len(filters["category"]) > 0:
            if "Category" in df.columns:
                df = df[df["Category"].isin(filters["category"])]
                print(f"      → After category filter: {len(df)} rows")
            else:
                print(f"      ⚠️  'Category' column not found in dataframe")
        else:
            print(f"      → Skipping category filter (all categories requested)")

    # Apply SKU filter
    if "sku" in filters and filters["sku"]:
        if "Sku" in df.columns:
            df = df[df["Sku"].isin(filters["sku"])]
            print(f"      → After SKU filter: {len(df)} rows")
        else:
            print(f"      ⚠️  'Sku' column not found in dataframe")
    
    if len(df) == 0:
        print(f"      ⚠️  No data left after filtering!")

    print(f"\n   🧮 Calculating metric: '{metric}'")
    
    # Ensure numeric columns are properly typed
    if "Final MRP Old" in df.columns:
        df["Final MRP Old"] = pd.to_numeric(df["Final MRP Old"], errors='coerce')
    if "TP" in df.columns:
        df["TP"] = pd.to_numeric(df["TP"], errors='coerce')
    
    if metric == "count":
        result = len(df)
    elif metric == "avg_mrp":
        if "Final MRP Old" in df.columns:
            result = df["Final MRP Old"].mean()
        else:
            result = None
            print(f"      ⚠️  'Final MRP Old' column not found")
    elif metric == "avg_tp":
        if "TP" in df.columns:
            result = df["TP"].mean()
        else:
            result = None
            print(f"      ⚠️  'TP' column not found")
    elif metric == "margin":
        if "Final MRP Old" in df.columns and "TP" in df.columns:
            result = (df["Final MRP Old"] - df["TP"]).mean()
        else:
            result = None
            print(f"      ⚠️  Required columns not found for margin calculation")
    elif metric == "stock_sum":
        result = stock_df["Stock"].sum()
    else:
        result = None
        print(f"      ⚠️  Unknown metric: {metric}")

    print(f"   ✅ Result: {result}")
    print("   [DATA AGENT] Complete!\n")

    return {"raw_result": result}