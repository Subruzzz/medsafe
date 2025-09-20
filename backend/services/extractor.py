from backend.services.ai_client import query_model

def extract_drug_names(text: str):
    prompt = f"""
Extract all medication names from the following text and return them as a JSON list:
{text}
Only include drug names, no explanations.
"""
    return query_model(prompt, max_tokens=150, temperature=0.0)
