import os
import pandas as pd
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
import altair as alt
import pdfplumber # For PDF text extraction

# --- Configuration ---
st.set_page_config(
    page_title="Project Insight: AI-Powered Document Analysis", # Updated title
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API Key not found. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- Helper Functions ---
@st.cache_data(show_spinner=False)
def load_data(uploaded_file):
    """Loads CSV, Excel, or PDF text content into a DataFrame."""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    try:
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ('.xlsx', '.xls'):
            df = pd.read_excel(uploaded_file)
        elif file_extension == '.pdf':
            with st.spinner("Extracting text from PDF... This may take a moment."):
                uploaded_file.seek(0) # Ensure file pointer is at the beginning
                all_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            all_text += page_text + "\n\n" # Add line breaks between pages

                if all_text.strip():
                    # Create a DataFrame with the extracted text
                    df = pd.DataFrame({"text_content": [all_text.strip()]})
                    st.success("Successfully extracted text from PDF.")
                else:
                    st.error("No readable text could be extracted from the PDF. It might be an image-based PDF or corrupted.")
                    return None
        else:
            st.error("Unsupported file type. Please upload a CSV, XLSX, XLS, or PDF file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}. Please ensure it's a valid CSV, Excel, or readable PDF file.")
        return None

@st.cache_resource(show_spinner=False)
def get_gemini_model():
    """Initializes and returns the Gemini model."""
    try:
        return genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    except Exception as e:
        st.error(f"Error initializing Gemini model: {e}")
        return None

# Function to extract JSON from LLM response
def extract_chart_json(response_text):
    match = re.search(r'```json\n({.*?})\n```', response_text, re.DOTALL)
    if match:
        try:
            chart_spec = json.loads(match.group(1))
            return chart_spec
        except json.JSONDecodeError:
            print("Error decoding JSON from LLM response.")
            return None
    return None

# --- Initialize Session State ---
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# --- Streamlit UI ---

# Sidebar
with st.sidebar:
    st.image("image.png", width=80)
    st.markdown("## Project Insight")
    st.markdown("""
        Unlock insights from your data using the power of Generative AI.
        Simply upload your file and ask questions in natural language.
    """)
    st.markdown("---")
    st.markdown("### How it Works:")
    st.info("""
        1.  **Upload:** Provide your CSV, Excel, or PDF document.
        2.  **Preview:** See the first few rows (for tabular) or confirmation of text extraction.
        3.  **Ask:** Type your questions about the content. The AI can even suggest charts if it finds numerical data!
        4.  **Analyze:** Gemini AI generates insights and optionally visualizations!
    """)
    st.markdown("---")
    st.caption("Powered by Gemini & Streamlit")

# Main Content Area
st.title("AI-Powered Document Analysis") # Updated title
st.markdown("""
    Upload your CSV, Excel, or PDF document and let Gemini help you understand its content better.
""")

# File Uploader Section
st.subheader("Upload Your Document") # Updated subheader
uploaded_file = st.file_uploader(
    "Choose a file to begin analysis.",
    type=["csv", "xlsx", "xls", "pdf"],
    key="file_uploader",
    help="Supported formats: CSV, XLSX, XLS (for tabular data), PDF (for text or tables)."
)

if uploaded_file:
    if "df" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.df = load_data(uploaded_file)
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.user_question = ""

    df = st.session_state.df

    if df is not None:
        st.success("File loaded successfully!")

        # Dynamic preview based on file type
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == '.pdf':
            st.markdown("### PDF Text Content (First 500 characters)")
            # Displaying first 500 characters of the extracted text for PDF
            if 'text_content' in df.columns and not df['text_content'].empty:
                st.text_area("Extracted Text Preview", df['text_content'].iloc[0][:500] + "...", height=150, disabled=True)
                st.info("Full PDF text content has been loaded for analysis.")
            else:
                st.warning("No text content available for preview.")
        else:
            with st.expander("Click to view Dataset Preview (first 10 rows)"):
                st.dataframe(df.head(10), use_container_width=True)
                st.info(f"Dataset has **{df.shape[0]} rows** and **{df.shape[1]} columns**.")

        # Question Input Section
        st.subheader("Ask a Question About Your Document") # Updated subheader

        col1, col2 = st.columns([0.8, 0.2])

        with col1:
            st.text_input(
                "What do you want to know about your document?", # Updated prompt
                placeholder="e.g., 'Summarize the document', 'What are the key responsibilities mentioned?', 'If this were tabular data, what would be the average of [column]?', 'Can you find a bar chart for [category] if present?'",
                key="user_question",
                label_visibility="collapsed"
            )

        with col2:
            def clear_query():
                st.session_state.user_question = ""
            st.button("Clear Query", on_click=clear_query, help="Clear the current question", type="secondary")

        question = st.session_state.user_question

        if st.button("Get Insight", type="primary"):
            if question:
                with st.spinner("Generating insights and visualizations with Gemini..."):
                    try:
                        # --- Dynamic Data Sample for Prompt ---
                        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                        data_for_llm = None # Initialize to None

                        if file_extension == '.pdf':
                            if 'text_content' in df.columns and not df['text_content'].empty:
                                data_for_llm = df['text_content'].iloc[0]
                                data_format_desc = "text content from the document"
                            else:
                                st.error("Could not find text content in the DataFrame for PDF analysis. Cannot proceed with AI analysis.")
                                st.stop() # Stop execution if data is not available for PDF
                        else: # CSV or Excel
                            data_for_llm = df.sample(min(20, len(df))).to_csv(index=False) if len(df) > 20 else df.to_csv(index=False)
                            data_format_desc = "sample of the dataset, formatted as a CSV string"

                        if data_for_llm is None: # Double-check if data_for_llm was set
                            st.error("Failed to prepare data for AI analysis.")
                            st.stop()

                        model = get_gemini_model()
                        if model:
                            # Adjust chart instruction based on data type
                            chart_instruction = ""
                            if file_extension != '.pdf': # Only give detailed chart instructions for tabular data
                                chart_instruction = """
                                If a data visualization is appropriate for the question, first output a JSON object with the chart specifications.
                                If the chart type is not explicitly requested, infer the most suitable chart type from the question and data.
                                The JSON should be enclosed in triple backticks and `json` tag like this:
                                ```json
                                {{
                                  "chart_type": "bar" | "line" | "scatter" | "histogram",
                                  "x_column": "column_name",
                                  "y_column": "column_name" | null,
                                  "aggregation": "sum" | "average" | "count" | null,
                                  "title": "Chart Title (Optional)"
                                }}
                                ```
                                Valid `chart_type` values are "bar", "line", "scatter", "histogram".
                                - For "bar" charts, `x_column` is typically categorical and `y_column` (if provided) is quantitative for aggregation. If `y_column` is null, assume count.
                                - For "line" charts, `x_column` is typically temporal or ordinal, and `y_column` is quantitative.
                                - For "scatter" charts, both `x_column` and `y_column` are quantitative.
                                - For "histogram" charts, only `x_column` is needed (quantitative). `y_column` and `aggregation` should be null.
                                Ensure column names in JSON exactly match those in the dataset.
                                If no chart is suitable, do not include the JSON block.

                                After the JSON (if present),
                                """
                            else: # For PDF text, charts are less likely, still allow if inferable
                                chart_instruction = """
                                If the question implies a visualization of structured (e.g., numerical or categorical) data that can be inferred from the text, first output a JSON object with the chart specifications. Otherwise, do not include a JSON block.
                                The JSON should follow the same format as for tabular data.
                                Use column names that best represent the inferred data. If no chart is suitable, do not include the JSON block.

                                After the JSON (if present),
                                """


                            prompt = f"""
                            You are an expert data analyst and document summarizer. Below is the {data_format_desc}:
                            ```
                            {data_for_llm}
                            ```

                            Based on this content, please perform the requested analysis.
                            {chart_instruction}
                            Provide a comprehensive explanation and analysis in natural language, including how the answer was derived from the content and any relevant context or limitations (e.g., if analyzing text, note it's based on inferred data).
                            Do not provide any code outside of the specified JSON block (if applicable).

                            Question: "{question}"
                            """
                            response = model.generate_content(prompt)
                            full_response_text = response.text

                            chart_spec = extract_chart_json(full_response_text)
                            cleaned_response_text = re.sub(r'```json\n({.*?})\n```', '', full_response_text, flags=re.DOTALL).strip()


                            st.subheader("Your Insight")
                            if chart_spec:
                                # For PDFs that are text-based, the dataframe might only have 'text_content' column.
                                # Charting will only work if the LLM *invented* relevant columns
                                # or if the text had embedded tables that pdfplumber missed but LLM could parse.
                                # This is a complex scenario, but we try to handle it gracefully.

                                try:
                                    st.write("Here is a visualization based on your query:")
                                    chart_type = chart_spec.get('chart_type')
                                    x_column = chart_spec.get('x_column')
                                    y_column = chart_spec.get('y_column')
                                    aggregation = chart_spec.get('aggregation')
                                    chart_title = chart_spec.get('title') or f"{x_column} vs {y_column if y_column else 'Count'}"

                                    # For text-based PDFs, charting is highly experimental and relies on LLM
                                    # correctly inferring or structuring data from prose.
                                    # If the AI suggests a chart for a text PDF, we'll try to generate it,
                                    # but warn the user that it's experimental.
                                    if file_extension == '.pdf':
                                        st.warning("Chart generation for purely text-based PDFs is experimental and relies on the AI inferring structured data from text. It may not always work as expected, especially if data is not explicitly tabular.")
                                        # To make charts work reliably for text PDFs, the LLM would need to
                                        # output the *data* in a structured format (e.g., a small CSV string)
                                        # which we then parse into a temporary DataFrame for Altair.
                                        # This current implementation attempts to use the main `df`, which for PDFs
                                        # only contains `text_content`. So, unless the LLM suggests `x_column` as
                                        # 'text_content' (e.g., for character counts), it won't find the columns.
                                        # For now, if the LLM suggests columns not in the DF, it will fall back to text.

                                    # IMPORTANT: Check if columns exist in the DataFrame *before* trying to plot.
                                    # This is crucial for both tabular and inferred-from-text data.
                                    chart_valid = True
                                    if x_column and x_column not in df.columns:
                                        st.warning(f"Chart: X-axis column '{x_column}' not found in data. Skipping chart generation.")
                                        chart_valid = False
                                    if y_column and y_column not in df.columns:
                                        st.warning(f"Chart: Y-axis column '{y_column}' not found in data. Skipping chart generation.")
                                        chart_valid = False

                                    if chart_spec and chart_valid and x_column: # Proceed only if spec is valid and columns exist
                                        chart = None
                                        if chart_type == "bar":
                                            if y_column and aggregation:
                                                chart = alt.Chart(df).mark_bar().encode(
                                                    x=alt.X(x_column, type='nominal'),
                                                    y=alt.Y(f'{aggregation}({y_column})', title=f'{aggregation.capitalize()} of {y_column}'),
                                                    tooltip=[x_column, alt.Tooltip(f'{aggregation}({y_column})')]
                                                ).properties(title=chart_title)
                                            else:
                                                chart = alt.Chart(df).mark_bar().encode(
                                                    x=alt.X(x_column, type='nominal'),
                                                    y=alt.Y('count()', title='Count of Records'),
                                                    tooltip=[x_column, 'count()']
                                                ).properties(title=chart_title)
                                        elif chart_type == "line" and y_column:
                                            x_type = 'quantitative' if pd.api.types.is_numeric_dtype(df[x_column]) else 'nominal'
                                            y_type = 'quantitative' if pd.api.types.is_numeric_dtype(df[y_column]) else 'nominal'
                                            chart = alt.Chart(df).mark_line().encode(
                                                x=alt.X(x_column, type=x_type),
                                                y=alt.Y(y_column, type=y_type),
                                                tooltip=[x_column, y_column]
                                            ).properties(title=chart_title)
                                        elif chart_type == "scatter" and y_column:
                                            x_type = 'quantitative' if pd.api.types.is_numeric_dtype(df[x_column]) else 'nominal'
                                            y_type = 'quantitative' if pd.api.types.is_numeric_dtype(df[y_column]) else 'nominal'
                                            chart = alt.Chart(df).mark_point().encode(
                                                x=alt.X(x_column, type=x_type),
                                                y=alt.Y(y_column, type=y_type),
                                                tooltip=[x_column, y_column]
                                            ).properties(title=chart_title)
                                        elif chart_type == "histogram":
                                            if x_column:
                                                chart = alt.Chart(df).mark_bar().encode(
                                                    alt.X(x_column, bin=True, title=x_column),
                                                    alt.Y('count()', title='Frequency')
                                                ).properties(title=chart_title)
                                            else:
                                                st.warning("Histogram requires an x_column to be specified.")
                                                chart_spec = None # Invalidate chart
                                        else:
                                            st.warning(f"Unsupported chart type or missing required columns for chart: {chart_type}.")
                                            chart_spec = None # Invalidate chart

                                        if chart:
                                            st.altair_chart(chart, use_container_width=True)
                                        else:
                                            # If chart_spec was valid but chart couldn't be built (e.g., specific Altair error)
                                            st.warning("Could not generate chart with the provided specifications. Please try refining your question.")

                                except Exception as chart_e:
                                    st.error(f"An unexpected error occurred during chart generation: {chart_e}")
                                    st.info("The AI might have suggested an incompatible chart or columns for the current data. Please refine your question.")

                            if cleaned_response_text:
                                st.markdown(cleaned_response_text)
                            elif not chart_spec: # If no chart and no text, something went wrong
                                st.warning("The AI did not provide a textual insight or a valid chart specification.")


                    except Exception as e:
                        st.error(f"An error occurred during AI generation: {e}")
                        st.info("Please try rephrasing your question or check the console for details.")
            else:
                st.warning("Please enter a question to get insights!")
    else:
        st.error("Failed to load DataFrame. Please ensure the file format is correct and it contains valid data.")

else:
    st.info("Upload a CSV, Excel, or PDF file to get started with your document analysis!")
