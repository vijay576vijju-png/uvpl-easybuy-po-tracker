import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="AI PO Extractor", layout="wide")

# IMPORTANT: Replace the text below with your actual Gemini API Key
# You can get it from: https://aistudio.google.com/app/apikey
API_KEY = "AIzaSyD6HfD1Ny0-eDIN39cKVbGHvfae1Gv8y2s" 
genai.configure(api_key=API_KEY)

def extract_data_with_ai(text):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    You are a professional Purchase Order (PO) analyzer. 
    Extract the following details from the provided text and return ONLY a valid JSON object.
    
    Fields to extract: 
    - PO Number
    - PO Date
    - Delivery Date
    - Style Description
    - Location
    - Quantity
    - Total Value

    If a field is missing in the text, use "Not Found" as the value.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI DESIGN ---
st.title("📦 Smart Customer PO Tracker")
st.markdown("### Upload your PO PDF to automatically extract details")
st.info("This tool uses AI to read different customer formats.")

uploaded_file = st.file_uploader("Upload PO PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner('AI is analyzing the PDF... Please wait.'):
        # Read text from the uploaded PDF
        full_text = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            
            # Send text to AI
            raw_ai_output = extract_data_with_ai(full_text)
            
            # Clean and parse JSON from AI response
            clean_json = raw_ai_output.replace("```json", "").replace("```", "").strip()
            data_dict = json.loads(clean_json)
            
            # Display results in a table
            df = pd.DataFrame([data_dict])
            st.success("Data Extracted Successfully!")
            st.write("---")
            st.subheader("Extracted Data Table")
            st.dataframe(df, use_container_width=True)
            
            # Export Option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data as CSV/Excel",
                data=csv,
                file_name="po_summary.csv",
                mime="text/csv",
            )
            
        except Exception as e:
            st.error("Error: Could not process the document. Check if your API Key is valid.")
            st.write("System Message:", e)
