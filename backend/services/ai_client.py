import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
IBM_MODEL_ID = os.getenv("IBM_MODEL_ID", "ibm-granite/granite-13b-chat-v2")

API_URL = f"https://api-inference.huggingface.co/models/{IBM_MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_model(prompt: str, max_tokens=400, temperature=0.7):
    if not HF_API_TOKEN:
        raise ValueError("Hugging Face API token not found in environment variables.")
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    return str(data)
