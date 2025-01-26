import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from typing import List

st.set_page_config(page_title="craigdoesdata | AI Chat", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    api_provider = st.selectbox(
        "Select API Provider",
        ["Google Gemini 2.0 Flash", "Deepseek Chat", "OpenAI GPT-4o", "Anthropic Claude"]
    )
    # Only show API key input for OpenAI and Anthropic
    if api_provider in ["OpenAI GPT-4o", "Anthropic Claude"]:
        api_key = st.text_input(f"Enter your {api_provider} API Key:", type="password")
    elif api_provider == "Google Gemini 2.0 Flash":
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.secrets["DEEPSEEK_API_KEY"]

    # Add Temperature Slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,  # Default temperature
        step=0.1,
        help="Controls the randomness of the output. Lower values like 0.2 make the output more focused and deterministic, while higher values like 0.9 make the output more random and creative."
    )

def generate_response(messages: List[dict], api_key: str, provider: str, temperature: float) -> str: # Added temperature parameter
    if not api_key:
        return "Please enter your API key in the sidebar."

    try:
        if provider == "Google Gemini 2.0 Flash":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

            # Convert message history to text format
            conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = model.generate_content(conversation) # Gemini API does not have explicit temperature parameter here.

            return response.text


        elif provider == "Deepseek Chat":
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature, # Use the temperature parameter
            )
            return response.choices[0].message.content

        elif provider == "OpenAI GPT-4o":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                store=True,
                messages=messages,
                temperature=temperature, # Use the temperature parameter
            )
            return response.choices[0].message.content

        elif provider == "Anthropic Claude":
            client = Anthropic(api_key=api_key)
            formatted_messages = []
            for msg in messages:
                if msg["role"] != "system":
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    formatted_messages.append({"role": role, "content": msg["content"]})

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=formatted_messages,
                max_tokens=1000,
                temperature=temperature # Use the temperature parameter
            )
            return response.content[0].text

    except Exception as e:
        return f"Error: {str(e)}"

st.title("craigdoesdata | AI Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("What would you like to discuss?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        response = generate_response(st.session_state.messages, api_key, api_provider, temperature) # Pass temperature here
        if response:
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})