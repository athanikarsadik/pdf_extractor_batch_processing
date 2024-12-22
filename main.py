# pdf_extractor/main.py
import streamlit as st
import openai
from app.streamlit_ui import setup_openai_api_key, display_api_key_settings, display_file_uploader, process_uploaded_files

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="PDF Extractor")
    setup_openai_api_key()
    display_api_key_settings()

    total_input_tokens = 0
    total_output_tokens = 0

    uploaded_files = display_file_uploader()
    submit = st.button("Analyze the Documents")

    if submit:
        process_uploaded_files(uploaded_files, total_input_tokens, total_output_tokens)

if __name__ == "__main__":
    main()