import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart PO Extractor", layout="wide")

# Your actual API Key from the screenshot
API_KEY = "AIzaSyD6HfD1Ny0-eDIN39cKVbGhvfae1Gv8y2s" 
genai.configure(api_key=API_KEY)

def extract_data_with_ai(text):
    # Using flash model for better reliability
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Extract the following details from this PO text and return ONLY a valid JSON object.
    Fields: PO Number, PO Date, Delivery Date, Style Description, Location, Quantity, Total Value.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI ---
st.title("📦 Smart Customer PO Tracker")

uploaded_file = st.file_uploader("Upload PO PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner('AI is reading the PO...'):
        try:
            full_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            
            raw_output = extract_data_with_ai(full_text)
            clean_json = raw_output.replace("```json", "").replace("```", "").strip()
            data_dict = json.loads(clean_json)
            
            df = pd.DataFrame([data_dict])
            st.success("Extraction Complete!")
            st.table(df)
            
        except Exception as e:
            st.error(f"Error: {e}")
