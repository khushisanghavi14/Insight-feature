import os
import pandas as pd
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Title and description
st.title("Project Insight")
#st.write("Upload a CSV file and ask questions about it using natural language.")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of Dataset")
    st.dataframe(df.head(10))

    # User inputs question
    question = st.text_input("Ask a question")

    if question:
        # Convert limited data to string
        data_string = df.head(20).to_csv(index=False)
        prompt = f"Here is a sample of the dataset:\n{data_string}\n\nNow, {question}"

        try:
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
            response = model.generate_content(prompt)
            st.subheader("Response")
            st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
