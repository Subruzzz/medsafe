from backend.services.ai_client import query_model

def explain_alternatives(drug_name: str, alternatives: list):
    prompt = f"""
The drug '{drug_name}' has the following alternatives: {alternatives}.
Explain in simple terms why these alternatives might be considered, 
including any differences in form, dosage, or side effects.
"""
    return query_model(prompt)
