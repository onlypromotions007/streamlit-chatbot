import streamlit as st
from openai import OpenAI
from typing import List

st.set_page_config(page_title="Personal AI Chat", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    api_key = st.text_input("Enter your DeepSeek API Key:", type="password")

def generate_response(messages: List[dict], api_key: str) -> str:
    if not api_key:
        return "Please enter your API key in the sidebar."
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

st.title("Personal AI Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("What would you like to discuss?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    if api_key:
        with st.chat_message("assistant"):
            response = generate_response(st.session_state.messages, api_key)
            st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})