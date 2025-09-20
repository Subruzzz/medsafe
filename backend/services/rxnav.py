import requests
from typing import List, Dict, Any, Optional

BASE = "https://rxnav.nlm.nih.gov/REST"

def name_to_rxcui(drug_name: str) -> Optional[str]:
    params = {"term": drug_name, "maxEntries": 1}
    r = requests.get(f"{BASE}/approximateTerm.json", params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("approximateGroup", {}).get("candidate", [])
    if not candidates:
        return None
    return candidates[0].get("rxcui")

def names_to_rxcuis(drug_names: List[str]) -> List[str]:
    rxcuis = []
    for n in drug_names:
        rxcui = name_to_rxcui(n)
        if rxcui:
            rxcuis.append(rxcui)
    return list(dict.fromkeys(rxcuis))

def interactions_for_rxcuis(rxcuis: List[str]) -> Dict[str, Any]:
    if len(rxcuis) < 2:
        return {"fullInteractionTypeGroup": []}
    params = {"rxcuis": "+".join(rxcuis)}
    r = requests.get(f"{BASE}/interaction/list.json", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def rxcui_label(rxcui: str) -> Optional[str]:
    r = requests.get(f"{BASE}/rxcui/{rxcui}/properties.json", timeout=15)
    if r.status_code != 200:
        return None
    props = r.json().get("properties", {})
    return props.get("name")

def ingredient_rxcuis(rxcui: str) -> List[str]:
    params = {"tty": "IN,SIN,PIN"}
    r = requests.get(f"{BASE}/rxcui/{rxcui}/related.json", params=params, timeout=15)
    r.raise_for_status()
    groups = r.json().get("relatedGroup", {}).get("conceptGroup", []) or []
    out = []
    for g in groups:
        for c in g.get("conceptProperties", []) or []:
            out.append(c.get("rxcui"))
    return list(dict.fromkeys([x for x in out if x]))

def products_for_ingredient(ing_rxcui: str) -> List[Dict[str, str]]:
    params = {"tty": "SCD,SBD"}
    r = requests.get(f"{BASE}/rxcui/{ing_rxcui}/related.json", params=params, timeout=20)
    r.raise_for_status()
    groups = r.json().get("relatedGroup", {}).get("conceptGroup", []) or []
    out = []
    for g in groups:
        for c in g.get("conceptProperties", []) or []:
            out.append({"rxcui": c.get("rxcui"), "name": c.get("name")})
    seen = set()
    uniq = []
    for item in out:
        if item["name"] not in seen:
            uniq.append(item)
            seen.add(item["name"])
    return uniq
