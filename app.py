import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
from typing import List

st.set_page_config(page_title="craigdoesdata | AI Chat", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    api_provider = st.selectbox(
        "Select API Provider",
        ["Deepseek Chat", "OpenAI GPT-4o", "Anthropic Claude"]
    )
    api_key = st.text_input(f"Enter your {api_provider} API Key:", type="password")

def generate_response(messages: List[dict], api_key: str, provider: str) -> str:
    if not api_key:
        return "Please enter your API key in the sidebar."
    
    try:
        if provider == "Deepseek Chat":
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content

        elif provider == "OpenAI GPT-4o":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                store=True,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content

        elif provider == "Anthropic Claude":
            client = Anthropic(api_key=api_key)
            # Convert message format for Anthropic
            formatted_messages = []
            for msg in messages:
                if msg["role"] != "system":  # Skip system messages for Anthropic
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    formatted_messages.append({"role": role, "content": msg["content"]})
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=formatted_messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.content[0].text

    except Exception as e:
        return f"Error: {str(e)}"

st.title("craigdoesdata | AI Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to discuss?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    if api_key:
        with st.chat_message("assistant"):
            response = generate_response(st.session_state.messages, api_key, api_provider)
            if response:  # Only write if we got a valid response
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})