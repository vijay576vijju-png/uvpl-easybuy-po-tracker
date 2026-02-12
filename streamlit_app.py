import streamlit as st
import google.generativeai as genai
import pdfplumber
import pandas as pd
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart PO Extractor", layout="wide")

st.title("Smart Customer PO Tracker")

# 🔐 Use Streamlit secret or manual input
API_KEY = st.text_input("Enter Gemini API Key", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)

def extract_data_with_ai(text):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
Extract the following details from this Purchase Order text.
Return ONLY valid JSON.
Do not add explanation.

Fields:
- PO Number
- PO Date
- Delivery Date
- Style Description
- Location
- Quantity
- Total Value

Text:
{text}
"""

    response = model.generate_content(prompt)
    return response.text


uploaded_file = st.file_uploader("Upload PO PDF", type="pdf")

if uploaded_file is not None and API_KEY:

    with st.spinner("AI is analyzing the document..."):
        try:
            # 1️⃣ Extract text from PDF
            full_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"

            if not full_text.strip():
                st.error("No text found in PDF.")
            else:
                # 2️⃣ Get AI Output
                raw_output = extract_data_with_ai(full_text)

                # 3️⃣ Clean JSON
                clean_json = raw_output.strip()
                clean_json = clean_json.replace("```json", "").replace("```", "").strip()

                # 4️⃣ Convert to dictionary
                data_dict = json.loads(clean_json)

                # 5️⃣ Display result
                df = pd.DataFrame([data_dict])

                st.success("Extraction Successful!")
                st.dataframe(df)

        except json.JSONDecodeError:
            st.error("AI did not return valid JSON. Try again.")
        except Exception as e:
            st.error("Processing failed.")
            st.write("Error:", e)
