import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
# Default to an IBM Granite model on Hugging Face if not set
IBM_MODEL_ID = os.getenv("IBM_MODEL_ID", "ibm-granite/granite-3.3-2b-instruct")

API_URL = f"https://api-inference.huggingface.co/models/{IBM_MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


class ChatbotService:
    """
    Chatbot service that uses an IBM Granite model hosted on Hugging Face.
    """

    def __init__(self, model_id: str = IBM_MODEL_ID):
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    def ask(self, prompt: str) -> str:
        """
        Sends a prompt to the IBM Granite model and returns the generated text.
        """
        if not HF_API_TOKEN:
            raise ValueError("Hugging Face API token not found in environment variables.")

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Hugging Face returns a list of dicts with 'generated_text'
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            else:
                return str(data)

        except requests.exceptions.RequestException as e:
            return f"Error communicating with IBM Granite model: {e}"


# Example usage (for testing only)
if __name__ == "__main__":
    bot = ChatbotService()
    reply = bot.ask("List possible side effects of ibuprofen.")
    print("Bot:", reply)
