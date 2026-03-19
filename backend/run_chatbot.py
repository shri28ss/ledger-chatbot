import sys
from chatbot import chatbot

# Set terminal encoding to UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def main():
    print("\n--- AI Expense Tracker Chatbot (Rule-Based) ---")
    print("--------------------------------------------------")
    print("Type 'exit' to quit.\n")
    
    # Updated to the user_id found in the database.
    suggested_user_id = "8db8b2ef-1ccb-49aa-8321-599f69d140b2"
    
    try:
        user_id_input = input(f"Enter Your User ID (Press Enter for: {suggested_user_id}): ").strip()
    except EOFError:
        user_id_input = suggested_user_id
        
    user_id = user_id_input if user_id_input else suggested_user_id
        
    print(f"\n✅ Active User ID: {user_id}")
    print("--------------------------------------------------")
    
    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
                
            response = chatbot(query, user_id)
            print(f"\nBot: {response}")
            print("--------------------------------------------------")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            # For debugging, we show more info
            import traceback
            traceback.print_exc()
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
