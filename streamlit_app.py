import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart PO Extractor", layout="wide")

# IMPORTANT: Make sure there are NO spaces inside the quotes with your key
API_KEY = "AIzaSyD6HfD1Ny0-eDIN39cKVbGhvfae1Gv8y2s" 

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("API Configuration Error.")

def extract_data_with_ai(text):
    # Using 'gemini-pro' as it is the most compatible name for older API versions
    # If this fails, change it back to 'gemini-1.5-flash'
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Extract the following details from this Purchase Order text and return ONLY a valid JSON object.
    Fields: PO Number, PO Date, Delivery Date, Style Description, Location, Quantity, Total Value.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- USER INTERFACE ---
st.title("📦 Smart Customer PO Tracker")

uploaded_file = st.file_uploader("Upload PO PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner('AI is analyzing the document...'):
        try:
            # 1. Extract text from PDF
            full_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            
            # 2. Get AI Output
            raw_output = extract_data_with_ai(full_text)
            
            # 3. Clean and Parse JSON
            # Removing any markdown formatting like ```json ... ```
            clean_json = raw_output.strip().replace("```json", "").replace("```", "")
            data_dict = json.loads(clean_json)
            
            # 4. Display Result
            df = pd.DataFrame([data_dict])
            st.success("Extraction Successful!")
            st.table(df)
            
        except Exception as e:
            st.error("Processing failed. Please check if your API key is active in Google AI Studio.")
            st.info(f"Technical Details: {e}")
