# pdf_extractor/app/streamlit_ui.py
import streamlit as st
from datetime import datetime
import os
import pandas as pd
from .data_extractor import extract_text_from_pdf, ats_extractor
from utils.excel_utils import save_to_excel
from config import load_api_key, save_api_key
import openai

def setup_openai_api_key():
    """Sets up the OpenAI API key in the Streamlit session state."""
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = load_api_key()
    openai.api_key = st.session_state.openai_api_key

def display_api_key_settings():
    """Displays the API key settings in the sidebar."""
    st.sidebar.header("Settings")
    new_api_key = st.sidebar.text_input("OpenAI API Key", "", type="password")
    if st.sidebar.button("Update API Key"):
        if new_api_key:
            st.session_state.openai_api_key = new_api_key
            openai.api_key = new_api_key
            save_api_key(new_api_key)
            st.success("API Key updated and saved successfully!")
    if st.session_state.openai_api_key:
        st.sidebar.write("Current API Key:", "****" + st.session_state.openai_api_key[-4:])

def display_file_uploader():
    """Displays the file uploader for PDF files."""
    st.header("Extract Information from Multiple PDFs")
    uploaded_files = st.file_uploader("Choose PDF files...", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        st.write(f"{len(uploaded_files)} PDF files uploaded successfully.")
    return uploaded_files

def process_uploaded_files(uploaded_files, total_input_tokens, total_output_tokens):
    """Processes the uploaded PDF files and extracts information."""
    if uploaded_files:
        try:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"output_{current_time}.xlsx"

            if not os.path.exists(excel_filename):
                with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                    pd.DataFrame().to_excel(writer, sheet_name='Extracted Data', index=False)

            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    temp_file_path = f"temp_uploaded_file_{uploaded_file.name}.pdf"
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    filename = uploaded_file.name
                    country_code = filename[4:6]

                    pdf_text, detected_language, input_tokens_img, output_tokens_img = extract_text_from_pdf(temp_file_path, country_code, total_input_tokens, total_output_tokens)
                    total_input_tokens += input_tokens_img
                    total_output_tokens += output_tokens_img

                    if pdf_text.strip():
                        extracted_data = ats_extractor(pdf_text, total_input_tokens, total_output_tokens)
                        saved_excel = save_to_excel(excel_filename, extracted_data, filename)
                        if saved_excel:
                            st.success(f"Data from {filename} saved successfully.")
                    else:
                        st.error(f"No text extracted from {filename}. Please check the file.")

                    os.remove(temp_file_path)

        except Exception as e:
            st.error(f"Error processing the documents: {e}")
    else:
        st.error("Please upload valid PDF files.")