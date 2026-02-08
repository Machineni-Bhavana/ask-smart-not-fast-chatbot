import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def main():
    api_key = "AIzaSyDexGHHlY0nEs4Hc0-U7j3ljow5cR5jUj8"
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return

    # Use the specific model requested
    model = "gemini-2.5-flash-lite"
    
    try:
        client = genai.Client(api_key=api_key)
        # Create chat with configuration for system instruction
        config = types.GenerateContentConfig(
            system_instruction="You are a helpful assistant designed to help users ask better questions. Instead of simply answering their queries directly, you should analyze their question and ask clarifying or probing questions that help specifically refine the scope, intent, or context of their inquiry. Guide them via the Socratic method to formulate a more precise and effective question."
        )
        chat_session = client.chats.create(model=model, config=config)
        
        print(f"Chatbot initialized: 'A Chatbot That Asks Better Questions'")
        print("Model:", model)
        print("Type 'quit', 'exit', or 'bye' to end the session.")

        while True:
            try:
                user_input = input("You: ")
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Bot: Goodbye!")
                    break
                
                response = chat_session.send_message(user_input)
                print(f"Bot: {response.text}")
                
            except KeyboardInterrupt:
                print("\nBot: Goodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")

if __name__ == "__main__":
    main()
