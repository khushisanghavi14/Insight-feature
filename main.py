import os
import pandas as pd
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Set page config
st.set_page_config(
    page_title="Project Insight",
    layout="wide"
)

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Sidebar
with st.sidebar:
    st.title("📊 Project Insight")
    st.markdown("Natural Language Data Analysis")
    st.markdown("---")
    st.markdown("Upload a CSV file and ask questions about your dataset using natural language.")

# Main Section
st.markdown("### Upload your data and ask")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Show data preview
        st.markdown("### Dataset Preview (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        # Ask question
        st.markdown("### Ask a Question About Your Data")
        question = st.text_input("Enter your question")

        if question:
            with st.spinner("Generating response..."):
                # Provide structure and sample to Gemini
                structure = f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns. Here are the column names: {list(df.columns)}."
                sample_data = df.to_string(index=False)

                prompt = f"{structure}\n\nHere is a sample of the data:\n{sample_data}\n\nQuestion: {question}"

                model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
                response = model.generate_content(prompt)

                st.markdown("### Response")
                st.write(response.text if hasattr(response, "text") else "No response returned.")

    except Exception as e:
        st.error(f"Failed to process file or generate response: {e}")
