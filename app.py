import streamlit as st
from ollama import Client

# 1. Page Configuration
st.set_page_config(page_title="Ollama Cloud Chatbot", page_icon="☁️")
st.title("Ollama Cloud Chatbot ☁️")

# 2. Sidebar for Authentication & Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    # Grab the API key securely via password input
    api_key = st.text_input("Ollama Cloud API Key", type="password", help="Get this from your ollama.com account settings.")
    # Set default model to a standard cloud model, but allow changing it
    model_name = st.text_input("Model Name", value="gpt-oss:20b-cloud", help="e.g., gpt-oss:20b-cloud, qwen3-coder:480b-cloud, etc.")
    
    st.markdown("---")
    st.markdown("Don't have a key? Get one from your [Ollama Account Settings](https://ollama.com).")

# Halt the app if no API key is provided
if not api_key:
    st.info("👋 Welcome! Please enter your Ollama Cloud API Key in the sidebar to get started.")
    st.stop()

# 3. Initialize the Ollama Client for the Cloud
# We point to the cloud host and pass the API key in the headers
client = Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {api_key}'} 
)

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Handle User Input
if prompt := st.chat_input(f"Send a message to {model_name}..."):
    
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and Stream the Assistant's Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Stream the response from Ollama Cloud
            response_stream = client.chat(
                model=model_name,
                messages=st.session_state.messages,
                stream=True
            )
            
            for chunk in response_stream:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌")
            
            # Remove the cursor when finished
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to Ollama Cloud: {e}")
            st.info("Check your API key and ensure you are using a valid cloud model name (e.g., must end with `-cloud` for some models).")