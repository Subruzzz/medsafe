import re
from typing import List, Dict
from backend.services.rxnav import name_to_rxcui, rxcui_label

def extract_candidate_drugs(text: str, max_phr_len: int = 3) -> List[str]:
    cleaned = re.sub(r"[\n\r\t]", " ", text)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-']+", cleaned)
    tokens = [t for t in tokens if not t.isdigit()]
    candidates = set()
    for n in range(1, max_phr_len + 1):
        for i in range(0, max(0, len(tokens) - n + 1)):
            phrase = " ".join(tokens[i:i+n])
            if len(phrase) < 3:
                continue
            if phrase.lower() in {"take", "tablet", "capsule", "daily", "mg", "bid", "tid", "prn"}:
                continue
            candidates.add(phrase)
    return list(candidates)

def resolve_drugs(text: str, limit: int = 20) -> List[Dict[str, str]]:
    candidates = extract_candidate_drugs(text)
    found = []
    for c in candidates[:200]:
        rxcui = name_to_rxcui(c)
        if rxcui:
            name = rxcui_label(rxcui) or c
            found.append({"query": c, "name": name, "rxcui": rxcui})
            if len(found) >= limit:
                break
    seen = set()
    result = []
    for item in found:
        if item["rxcui"] not in seen:
            result.append(item)
            seen.add(item["rxcui"])
    return result
