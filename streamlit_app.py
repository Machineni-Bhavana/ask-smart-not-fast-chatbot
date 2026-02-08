import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def get_gemini_client():
    api_key = "AIzaSyDexGHHlY0nEs4Hc0-U7j3ljow5cR5jUj8"
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {e}")
        return None

import logging

# Suppress warnings from google.genai specific to AFC defaults if possible
logging.getLogger("google.genai").setLevel(logging.ERROR)

def main():
    st.set_page_config(page_title="Question Refiner Bot", page_icon="�")
    st.title("� A Chatbot That Asks Better Questions")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize client
    if "genai_client" not in st.session_state:
        st.session_state.genai_client = get_gemini_client()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question, and I'll help you refine it..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for exit commands
        if prompt.lower() in ["quit", "exit", "bye"]:
            with st.chat_message("assistant"):
                st.markdown("Goodbye! Keep asking great questions.")
            st.stop()

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            if st.session_state.genai_client:
                try:
                    # Reconstruct history for context
                    history = []
                    # st.session_state.messages contains ALL messages including the one just added
                    # We need to pass previous messages as history, and the last one via send_message
                    previous_messages = st.session_state.messages[:-1]
                    
                    for msg in previous_messages:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
                    
                    model = "gemini-2.5-flash-lite"
                    
                    # Create chat with history and system instruction
                    config = types.GenerateContentConfig(
                        system_instruction="You are a helpful assistant designed to help users ask better questions. Instead of simply answering their queries directly, you should analyze their question and ask clarifying or probing questions that help specifically refine the scope, intent, or context of their inquiry. Guide them via the Socratic method to formulate a more precise and effective question. Do not be annoying; be helpful and constructive."
                    )
                    
                    chat = st.session_state.genai_client.chats.create(
                        model=model,
                        config=config,
                        history=history
                    )
                    
                    import time
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            response = chat.send_message(prompt)
                            st.markdown(response.text)
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                            break
                        except Exception as e:
                            error_str = str(e)
                            if ("503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()) and attempt < max_retries - 1:
                                wait_time = 2 * (attempt + 1)
                                st.toast(f"Model overloaded. Retrying in {wait_time}s...", icon="⏳")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise e
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Client not initialized.")

if __name__ == "__main__":
    main()
