from dotenv import load_dotenv
from google import genai
import streamlit as st
import requests
import json
import os

def gemma_send(input_text, component_name):

    load_dotenv()
    gemma_key = os.getenv("GEMMA_KEY")

    client = genai.Client(api_key=gemma_key)
    # initial_prompt = f"You are an expert at creating beautiful clean API documentation in the style of ShadCN. Make me a thorough piece of api documentation in the style of shadcn that is a react component that is exported as default with the name {component_name}(and only return to me the code) so i can render it on a webpage for this code: "
    initial_prompt = f"You are an expert at creating beautiful clean API documentation in the style of ShadCN. Make me a thorough piece of API documentation in the style of ShadCN that is a React component requiring no external dependencies and exported as default with the name {component_name}. Only return the plain code as text (do not wrap it in markdown code fences or include any syntax highlighting) so I can render it on a webpage for this code: "
    try:
        response = client.models.generate_content(
            model=  "gemini-2.0-flash-thinking-exp-01-21", # "gemini-2.0-flash", "gemini-2.5-pro-exp-03-25",
            contents=f"{initial_prompt}{input_text}"
        )
        result = response.json()
        if isinstance(result, str):
            result = json.loads(result)
        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None