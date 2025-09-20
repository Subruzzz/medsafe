from fastapi import FastAPI
from backend.services.chatbot import chatbot_reply
from backend.services.extractor import extract_drug_names
from backend.services.summarizer import summarize_interactions
from backend.services.alternatives import explain_alternatives

app = FastAPI()

@app.post("/chat")
def chat(prompt: str):
    return {"response": chatbot_reply(prompt)}

@app.post("/extract")
def extract(text: str):
    return {"drugs": extract_drug_names(text)}

@app.post("/summarize")
def summarize(data: str):
    return {"summary": summarize_interactions(data)}

@app.post("/alternatives")
def alternatives(drug: str, options: list):
    return {"explanation": explain_alternatives(drug, options)}
