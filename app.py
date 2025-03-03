import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests
import json
import time
from typing import List

st.set_page_config(page_title="craigdoesdata | AI Chat", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    api_provider = st.selectbox(
        "Select API Provider",
        ["Google Gemini 2.0 Flash Thinking", "Deepseek r1", "Deepseek Chat", "OpenAI GPT-4o", "Anthropic Claude", "EC2 Deepseek r1"]
    )
    # Only show API key input for OpenAI and Anthropic
    if api_provider in ["OpenAI GPT-4o", "Anthropic Claude"]:
        api_key = st.text_input(f"Enter your {api_provider} API Key:", type="password")
    elif api_provider == "Google Gemini 2.0 Flash Thinking":
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif api_provider == "EC2 Deepseek r1":
        api_key = "not_required"  # Not needed for the direct EC2 endpoint
        ec2_ip = st.text_input("Enter your EC2 instance IP address:", value="<your-ec2-public-ip>")
        stream_mode = st.checkbox("Enable streaming", value=True)
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
    
    # Add max tokens/length slider for EC2 instance
    if api_provider == "EC2 Deepseek r1":
        max_length = st.slider(
            "Max Length",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Maximum number of tokens to generate"
        )

def stream_response_from_ec2(ec2_ip, prompt, max_length, temperature):
    """Stream response from EC2 instance"""
    api_url = f"http://{ec2_ip}:8000/generate_stream"  # Note the stream endpoint
    data = {
        "prompt": prompt,
        "max_length": max_length,
        "temperature": temperature,
        "stream": True  # Ensure streaming is enabled
    }
    headers = {'Content-type': 'application/json'}
    
    try:
        # Using stream=True to get chunks as they arrive
        with requests.post(api_url, data=json.dumps(data), headers=headers, stream=True) as response:
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            # Create a placeholder for streaming content
            placeholder = st.empty()
            full_response = ""
            
            # Process each chunk as it arrives
            for chunk in response.iter_lines():
                if chunk:
                    # Parse the chunk as JSON
                    try:
                        chunk_data = json.loads(chunk.decode('utf-8'))
                        
                        # Check if this is a thought or a response
                        if "thought" in chunk_data:
                            # Show thoughts in italics or with a different style
                            chunk_text = f"*Thinking: {chunk_data['thought']}*\n\n"
                        elif "token" in chunk_data:
                            chunk_text = chunk_data['token']
                        elif "generated_text" in chunk_data:
                            chunk_text = chunk_data['generated_text']
                        else:
                            # Fallback for other formats
                            chunk_text = str(chunk_data)
                        
                        # Append to the full response
                        full_response += chunk_text
                        
                        # Update the display
                        placeholder.markdown(full_response)
                    except json.JSONDecodeError:
                        # If not valid JSON, try to display as text
                        decoded = chunk.decode('utf-8')
                        full_response += decoded
                        placeholder.markdown(full_response)
            
            return full_response
    except Exception as e:
        return f"Error streaming from EC2: {str(e)}"

def generate_response(messages: List[dict], api_key: str, provider: str, temperature: float, **kwargs) -> str:
    if provider != "EC2 Deepseek r1" and not api_key:
        return "Please enter your API key in the sidebar."

    try:
        if provider == "Google Gemini 2.0 Flash Thinking":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

            # Convert message history to text format
            conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = model.generate_content(conversation) # Gemini API does not have explicit temperature parameter here.

            return response.text

        elif provider == "Deepseek r1":
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages,
                temperature=temperature, # Use the temperature parameter
            )
            return response.choices[0].message.content

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
            
        elif provider == "EC2 Deepseek r1":
            ec2_ip = kwargs.get('ec2_ip', '<your-ec2-public-ip>')
            max_length = kwargs.get('max_length', 100)
            stream_mode = kwargs.get('stream_mode', False)
            
            # Format the last user message for the EC2 LLM
            last_user_message = ""
            for msg in messages:
                if msg["role"] == "user":
                    last_user_message = msg["content"]
            
            # If streaming is enabled, use the streaming function
            if stream_mode:
                return stream_response_from_ec2(ec2_ip, last_user_message, max_length, temperature)
            
            # Non-streaming fallback
            api_url = f"http://{ec2_ip}:8000/generate"
            data = {
                "prompt": last_user_message, 
                "max_length": max_length,
                "temperature": temperature
            }
            headers = {'Content-type': 'application/json'}
            
            response = requests.post(api_url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                return response.json()["generated_text"]
            else:
                return f"Error: {response.status_code}. Details: {response.text}"

    except Exception as e:
        return f"Error: {str(e)}"

# Display logo with link using markdown at the top of the page
st.markdown("""
<a href="https://www.craigdoesdata.com/">
    <img src="https://github.com/thecraigd/Python_SQL/raw/master/img/logo.png" alt="CraigDoesData Logo" width="300">
</a>
""", unsafe_allow_html=True)


st.title("AI Chatbot")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("What would you like to discuss?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        # Pass additional kwargs for EC2 instance if needed
        kwargs = {}
        if api_provider == "EC2 Deepseek r1":
            kwargs['ec2_ip'] = ec2_ip
            kwargs['max_length'] = max_length
            if 'stream_mode' in locals():
                kwargs['stream_mode'] = stream_mode
            
        response = generate_response(st.session_state.messages, api_key, api_provider, temperature, **kwargs)
        if response:
            # If not using streaming mode, display the response normally
            if api_provider != "EC2 Deepseek r1" or not kwargs.get('stream_mode', False):
                st.write(response)
            # For streaming mode, the response is already displayed, so just add to session state
            st.session_state.messages.append({"role": "assistant", "content": response})
