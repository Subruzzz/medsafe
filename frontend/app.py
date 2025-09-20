import os
import requests
import streamlit as st
import pandas as pd

API = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="MedSafe Demo", layout="wide")

st.markdown("### MedSafe Demo — Educational Only")
st.info("This tool is for learning and exploration. It is not medical advice. Always consult a licensed clinician.")

with st.sidebar:
    st.markdown("#### Patient context (optional)")
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=400.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0)
    st.caption("Context is displayed with results but does not produce dosing recommendations.")

tab1, tab2, tab3, tab4 = st.tabs(["Interactions", "Extract from text", "Alternatives", "Chatbot"])

with tab1:
    st.subheader("Multi-drug interaction checker")
    drug_list = st.text_area("Enter drug names (comma-separated)", placeholder="ibuprofen, paracetamol, amoxicillin")
    if st.button("Check interactions"):
        drugs = [d.strip() for d in drug_list.split(",") if d.strip()]
        if len(drugs) < 2:
            st.warning("Please enter at least two drugs.")
        else:
            try:
                r = requests.post(f"{API}/interactions", json={"drugs": drugs}, timeout=60)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error"))
                else:
                    data = r.json()
                    labels = data["labels"]
                    st.write(f"Patient context — Age: {age}y, Weight: {weight}kg, Height: {height}cm")
                    groups = data["data"].get("fullInteractionTypeGroup", []) or []
                    if not groups:
                        st.success("No known interactions found in the reference for the provided drugs.")
                    else:
                        for g in groups:
                            for fit in g.get("fullInteractionType", []) or []:
                                pairs = fit.get("interactionPair", []) or []
                                for p in pairs:
                                    desc = p.get("description", "")
                                    concepts = p.get("interactionConcept", []) or []
                                    names = []
                                    for c in concepts:
                                        rxcui = c.get("minConceptItem", {}).get("rxcui")
                                        label = labels.get(rxcui, rxcui)
                                        names.append(label)
                                    st.error(f"Potential interaction: {', '.join(names)}")
                                    st.write(desc)
            except Exception as e:
                st.error(f"Request failed: {e}")

with tab2:
    st.subheader("Extract likely drug names from text")
    sample = "Rx: Amoxicillin 500 mg TID for 7 days. Also taking ibuprofen PRN."
    rx_text = st.text_area("Paste prescription or notes", value=sample, height=150)
    if st.button("Extract drugs"):
        try:
            r = requests.post(f"{API}/extract", json={"text": rx_text}, timeout=60)
            r.raise_for_status()
            resolved = r.json()["resolved"]
            if not resolved:
                st.warning("No confident drug names found.")
            else:
                df = pd.DataFrame(resolved)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Extraction failed: {e}")

with tab3:
    st.subheader("Alternatives (same ingredient products)")
    name = st.text_input("Drug name", placeholder="ibuprofen")
    if st.button("Find alternatives"):
        if not name.strip():
            st.warning("Enter a drug name.")
        else:
            try:
                r = requests.get(f"{API}/alternatives", params={"drug": name.strip()}, timeout=60)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error"))
                else:
                    data = r.json()
                    alts = data.get("alternatives", [])
                    if not alts:
                        st.info("No alternatives found for the same ingredient.")
                    else:
                        df = pd.DataFrame(alts)
                        st.dataframe(df, use_container_width=True)
                        st.caption("Listed products share the same active ingredient; this is not a recommendation.")
            except Exception as e:
                st.error(f"Lookup failed: {e}")

with tab4:
    st.subheader("Chatbot")
    st.caption("Ask how to use the app or general non-medical questions. Medical questions will be refused.")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    user_input = st.text_input("Your message", "")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat.append({"role": "user", "content": user_input})
            try:
                r = requests.post(f"{API}/chat", json={"message": user_input}, timeout=60)
                r.raise_for_status()
                st.session_state.chat.append(r.json())
            except Exception as e:
                st.session_state.chat.append({"role": "assistant", "content": "Sorry, I had trouble responding."})
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.write(f"🧑‍💻: {msg['content']}")
        else:
            st.write(f"🤖: {msg['content']}")

st.divider()
st.markdown("#### Export session history")
if st.button("Download latest checks as CSV"):
    try:
        r = requests.get(f"{API}/history", timeout=30)
        r.raise_for_status()
        rows = r.json().get("history", [])
        if not rows:
            st.info("No history yet.")
        else:
            df = pd.DataFrame(rows)
            st.download_button("Save history.csv", df.to_csv(index=False), file_name="history.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Export failed: {e}")
