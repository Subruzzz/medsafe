from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from backend.services.rxnav import names_to_rxcuis, interactions_for_rxcuis, rxcui_label, ingredient_rxcuis, products_for_ingredient
from backend.services.extractor import resolve_drugs
from backend.services.chatbot import chat_reply
from backend.services.memory import SessionMemory
app = FastAPI(title="MedSafe Demo", version="0.1.0")
memory = SessionMemory(maxlen=25)

class InteractionRequest(BaseModel):
    drugs: List[str] = Field(..., description="List of drug names")

class ExtractRequest(BaseModel):
    text: str = Field(..., description="Unstructured prescription text")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message for chatbot")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/interactions")
def interactions(req: InteractionRequest):
    if not req.drugs or len(req.drugs) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two drug names.")
    rxcuis = names_to_rxcuis(req.drugs)
    if len(rxcuis) < 2:
        raise HTTPException(status_code=404, detail="Could not resolve enough drugs to RxNorm.")
    data = interactions_for_rxcuis(rxcuis)
    labels = {rc: (rxcui_label(rc) or rc) for rc in rxcuis}
    payload = {"rxcuis": rxcuis, "labels": labels, "data": data}
    memory.add_record({"type": "interaction_check", **payload})
    return payload

@app.get("/alternatives")
def alternatives(drug: str):
    from services.rxnav import name_to_rxcui
    rxcui = name_to_rxcui(drug)
    if not rxcui:
        raise HTTPException(status_code=404, detail="Drug not found")
    ing_rxcuis = ingredient_rxcuis(rxcui)
    if not ing_rxcuis:
        return {"drug": drug, "alternatives": []}
    all_products = []
    for ing in ing_rxcuis:
        all_products.extend(products_for_ingredient(ing))
    primary = rxcui_label(rxcui)
    alts = [p for p in all_products if p["name"] != primary]
    return {"drug": primary or drug, "alternatives": alts[:25]}

@app.post("/extract")
def extract(req: ExtractRequest):
    resolved = resolve_drugs(req.text)
    return {"resolved": resolved}

@app.post("/chat")
def chat(req: ChatRequest):
    reply = chat_reply(req.message)
    return reply

@app.get("/history")
def history():
    return {"history": memory.export_rows()}
