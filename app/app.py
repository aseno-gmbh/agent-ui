import streamlit as st
import requests
#from aleph_alpha_client import Client, CompletionRequest, Prompt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils import *

# open config file for references
with open('./app/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Authentifizierungsobjekt erstellen
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

# Logout button
if st.session_state['authentication_status']:
    st.sidebar.markdown(f"<h4 style='color: var(--text-color);'>Hello {st.session_state.name}</h4>", unsafe_allow_html=True)
    authenticator.logout("Logout", "sidebar")
# Streamlit App
    # List of models
    models = [model for model, settings in config['models'].items() if settings['enabled']]
    # Create a select box for the models
    st.sidebar.image("./images/cdlogo.png")
    st.sidebar.markdown('---')
    st.sidebar.title(f"Cloud Doctor Platform")
    st.sidebar.markdown('---')

    st.session_state["models"] = st.sidebar.selectbox("Which Model?:", models, index=0, on_change=on_change_callback)
    new_chat = st.sidebar.button("start new chat")
    if new_chat:
        st.session_state['messages'] = []  # Reset chat history
        st.rerun()
    
    # Page title
    st.markdown(f"<h1 style='text-align: center; color: var(--text-color);'> Cloud Doctor Chatbot </h1>", unsafe_allow_html=True)
    # Set up session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    user_prompt = st.chat_input("Enter your text", key="user_input")
    if user_prompt:
        # Display user input in chat message container    
        with st.chat_message("user"):
            st.markdown(user_prompt)
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        # Call the model and display results
        with st.spinner(f'Antwort wird generiert mit dem Sprachmodell: {st.session_state["models"]} ...'):
            with st.chat_message("assistant"):
                result= st.write_stream(stream_any_model(user_prompt, st.session_state["models"], st.session_state.messages))

        # Add model response to session state
        st.session_state.messages.append({"role": "assistant", "content": result})

elif st.session_state['authentication_status'] is False:
    st.error("Wrong Username or Password")
elif st.session_state['authentication_status'] is None:
    st.warning("Please login")