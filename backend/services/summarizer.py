from backend.services.ai_client import query_model

def summarize_interactions(raw_data: str):
    prompt = f"""
Summarize the following drug interaction data in plain, patient-friendly language:
{raw_data}
"""
    return query_model(prompt)
