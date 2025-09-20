from backend.services.ai_client import query_model

def chatbot_reply(user_message: str, context: str = ""):
    prompt = f"""
You are MedSafe, an AI medical assistant. 
Context: {context}
User: {user_message}
Provide a clear, concise, and safe response. Avoid giving medical advice beyond general information.
"""
    return query_model(prompt)
