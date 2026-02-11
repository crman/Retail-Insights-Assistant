import sys

# Load configuration (loads .env and sets API keys)
from configs import config  

# Now import graph and utilities
from graph import graph
from utils.db_utils import get_available_tables, get_table_preview


def select_table() -> str:
    """
    Display available tables and let user select one.
    """
    try:
        tables = get_available_tables()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("\nPlease run 'python sql/setup_database.py' first to create the database.")
        sys.exit(1)
    
    if not tables:
        print("ERROR: No tables found in database.")
        print("Please run 'python sql/setup_database.py' to load data.")
        sys.exit(1)
    
    print("Available Tables:")
    print("-" * 70)
    
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
        try:
            preview = get_table_preview(table)
            print(f"   {preview}")
        except Exception as e:
            print(f"   (Unable to load preview: {e})")
        print()
    
    while True:
        try:
            choice = input("Select table number: ").strip()
            table_idx = int(choice) - 1
            
            if 0 <= table_idx < len(tables):
                selected = tables[table_idx]
                print(f"\nSelected: {selected}")
                return selected
            else:
                print(f"WARNING: Please enter a number between 1 and {len(tables)}")
        except ValueError:
            print("WARNING: Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            sys.exit(0)


def select_mode() -> str:
    """
    Let user select operation mode.
    """
    print("\n" + "=" * 70)
    print("Select Mode:")
    print("1. QA - Ask specific questions about the data")
    print("2. Summary - Get an overall summary of the dataset")
    print("=" * 70)
    
    while True:
        try:
            choice = input("\nMode (1/2 or qa/summary): ").strip().lower()
            
            if choice in ['1', 'qa']:
                return 'qa'
            elif choice in ['2', 'summary']:
                return 'summary'
            else:
                print("WARNING: Please enter '1', '2', 'qa', or 'summary'")
                
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            sys.exit(0)


def get_question() -> str:
    """
    Get question from user.
    """
    while True:
        try:
            question = input("\nAsk your question: ").strip()
            
            if question:
                return question
            else:
                print("WARNING: Please enter a question")
                
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            sys.exit(0)


def main():
    # Select table
    table = select_table()
    
    # Main query loop
    while True:
        try:
            # Select mode
            mode = select_mode()
            
            # Get question if in QA mode
            question = ""
            if mode == 'qa':
                question = get_question()
            
            # Execute agent workflow
            print("\n" + "=" * 70)
            print(f"STARTING EXECUTION - Mode: {mode.upper()}")
            print("=" * 70)
            print()
            
            result = graph.invoke({
                "mode": mode,
                "table": table,
                "question": question,
                "table_schema": None,
                "sql_query": None,
                "raw_result": None,
                "final_answer": None
            })
            
            # Display final answer
            print("\n" + "=" * 70)
            print("ANSWER:")
            print("=" * 70)
            print(result["final_answer"])
            print("=" * 70)
            
            # Ask if user wants to continue
            print("\n")
            continue_choice = input("Ask another question? (y/n): ").strip().lower()
            
            if continue_choice not in ['y', 'yes']:
                print("\nGoodbye!")
                break
                
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nERROR: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()