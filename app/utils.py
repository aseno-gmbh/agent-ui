# import libraries
import streamlit as st
import requests
from aleph_alpha_client import Client, CompletionRequest, Prompt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import openai
from openai.types.chat import ChatCompletionChunk
from openai import OpenAI
from openai import AzureOpenAI
from typing import Generator
from envs import Settings
from prompt_templates import TEMPLATE_CD

# open config file for references
with open('./app/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# define prompt template:
#prompt_template_hf = "Du bist ein Wissensbot der Fragen im Gesundheitswesen beantworten soll. CD steht für Cloud Doctor. Verwende keine Obszönen Ausdrücke! "

def stream_any_model(prompt, model, history):
    conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
    full_prompt = f"{TEMPLATE_CD}\n {conversation}\n {prompt}"

    if config['models'].get(model).get("cloud") == "azure":
        client = AzureOpenAI(  
            azure_endpoint=str(Settings().AZURE_API_URL),  
            api_key=Settings().AZURE_API_KEY.get_secret_value(),
            api_version="2024-05-01-preview",
            )
    else:
        client = OpenAI(
            base_url= config['models'].get(model).get("url"),
            api_key = config['models'].get(model).get("token", "-")
            )
    
    modelname = config['models'].get(model).get("modelname")

    try:
        # Sending request to the OpenAI API
        response = client.chat.completions.create(
            model=modelname,
            messages=[
                {"role": "user",
                 "content": full_prompt}
            ],
            stream=True
        )
        

        for data in response:
            yield data
        
    except openai.OpenAIError as e:
        error_message = f"Error while streaming model output: {str(e)}"
        st.error(error_message)
        return error_message


# Delete Session State with previous messages when the LLM is changed in the Selectbox
def on_change_callback():
    st.session_state['messages'] = []  # Reset chat history