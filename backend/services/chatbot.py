import os
import requests
from typing import Dict

SAFETY_REFUSAL = (
    "I can’t provide medical advice, dosing, diagnosis, or urgent guidance. "
    "Use this app for education only and consult a licensed clinician."
)

HELP_TEXT = (
    "You can: 1) Enter multiple drug names to check potential interactions, "
    "2) Paste a prescription to extract likely drug names, "
    "3) View non-binding alternatives (same ingredient), and "
    "4) Export your session as CSV. This is not medical advice."
)

def is_medical_question(msg: str) -> bool:
    m = msg.lower()
    keywords = [
        "dose", "dosage", "how much", "take with", "take if", "pregnant",
        "breastfeed", "contraindication", "kidney", "liver", "interaction with",
        "can i take", "should i take", "is it safe", "side effect", "symptom",
        "treat", "cure", "diagnose", "blood pressure", "diabetes", "child", "baby"
    ]
    return any(k in m for k in keywords)

def chat_reply(message: str) -> Dict[str, str]:
    if is_medical_question(message):
        return {"role": "assistant", "content": SAFETY_REFUSAL}

    token = os.getenv("HUGGINGFACE_API_TOKEN", "").strip()
    if not token:
        return {"role": "assistant", "content": HELP_TEXT}

    endpoint = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    headers = {"Authorization": f"Bearer {token}"}
    prompt = (
        "You are a cautious assistant for a non-clinical drug interaction demo app. "
        "Never give medical advice or dosing. If asked medical questions, refuse. "
        "Answer briefly and helpfully about how to use the app. "
        f"User: {message}\nAssistant:"
    )
    try:
        r = requests.post(endpoint, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 128}}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            return {"role": "assistant", "content": data[0].get("generated_text", HELP_TEXT)}
        return {"role": "assistant", "content": HELP_TEXT}
    except Exception:
        return {"role": "assistant", "content": HELP_TEXT}
