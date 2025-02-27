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

# open config file for references
with open('./app/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# define prompt template:
prompt_template_hf = "Du bist ein Wissensbot der Fragen im Gesundheitswesen beantworten soll. CD steht für Cloud Doctor. Verwende keine Obszönen Ausdrücke! "

def stream_any_model(prompt, model, history):
    conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
    full_prompt = f"{prompt_template_hf}\n {conversation}\n {prompt}"

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

# # This function utilises the AzureOpenAI module which is why
# def stream_azure_model(prompt, model, history):
#     conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
#     full_prompt = f"{prompt_template_hf}\n {conversation}\n {prompt}"

#     client = AzureOpenAI(  
#         azure_endpoint=config['models'].get(model).get("url"),  
#         api_key=config['models'].get(model).get("token", "-"),
#         api_version="2024-05-01-preview",
#     )
    
#     modelname = config['models'].get(model).get("modelname")

#     try:
#         # Sending request to the OpenAI API
#         response = client.chat.completions.create(
#             model=modelname,
#             messages=[
#                 {"role": "user",
#                  "content": full_prompt}
#             ],
#             stream=True
#         )
    
#         for data in response:
#             yield data
        
#     except openai.OpenAIError as e:
#         error_message = f"Error while streaming model output: {str(e)}"
#         st.error(error_message)
#         return error_message

#https://llmaastestgerm3554682259.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-05-01-preview

# def interpret_stream(stream: Generator):
#     with st.spinner(text="Antwort wird generiert..."):
#         try:
#             while chunk := next(stream):
#                 if isinstance(chunk, ChatCompletionChunk):
#                     yield chunk
#                     break
#                 else:
#                     yield chunk
#         except StopIteration:
#             pass
#     for chunk in stream:
#         yield chunk

# # Function to query a VLLM model
# def query_any_model(prompt, model, history):
#     conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
#     full_prompt = f"{prompt_template_hf}\n {conversation}\n {prompt}"

#     url = config['models'].get(model).get("url")
#     modelname = config['models'].get(model).get("modelname")
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     data = {
#     "model": modelname,
#     "messages": [
#         {
#             "role": "user",
#             "content": full_prompt
#         }
#     ]
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
    
#         result = response.json()
#         result = result['choices'][0]['message']['content']
#     except requests.exceptions.RequestException as e:
#         error_message = str(e)
#         result = f"Error while requesting model: {error_message}"
#     return result


# # Function to query a VLLM deployment
# def query_model(prompt, history):
#     # Combine the history with the current prompt for contextual responses
#     conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
#     full_prompt = f"{conversation}\n {prompt_template}\n {prompt}"
#     return "Model return MOCK"

# # Query the Aleph Alpha Model
# def query_aleph_alpha(prompt, model, history):
#     conversation = "\n".join([f"{msg['content']}" if msg['role'] == "user" else f"{msg['content']}" for msg in history])
#     full_prompt = f"{prompt_template_aa}\n {conversation}\n {prompt}"
#     client = Client(token=config['models'].get(model).get("token"),
#                     host=config['models'].get(model).get("url"))
#     request = CompletionRequest(prompt=Prompt.from_text(full_prompt), maximum_tokens=500)
#     response = client.complete(request, model="pharia-1-llm-7b-control")
#     return response.completions[0].completion

# Delete Session State with previous messages when the LLM is changed in the Selectbox
def on_change_callback():
    st.session_state['messages'] = []  # Reset chat history