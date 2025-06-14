Project Insight: AI-Powered Document Analysis
Project Insight is a Streamlit web application that leverages Google's Gemini AI to provide natural language data analysis and insights from your documents. Whether you have structured data in CSV or Excel files, or extensive text in PDFs, this app aims to help you understand your content better by answering questions and even generating visualizations.

✨ Features
Multi-Format File Upload: Seamlessly upload data from:

CSV (.csv)

Excel (.xlsx, .xls)

PDF (.pdf) - Extracts text content from theoretical PDFs and tables from structured PDFs.

AI-Powered Q&A: Ask natural language questions about your uploaded data/document content.

Intelligent Insights: Gemini AI processes your query and the document/data to provide comprehensive textual explanations and answers.

Automatic Chart Generation: If your question implies a data visualization, the AI will intelligently suggest and generate relevant charts (e.g., bar, line, scatter, histogram) using Altair, particularly effective with tabular data.

Clear Query Functionality: Easily clear your input question with a dedicated button.

Responsive UI: Built with Streamlit for an interactive and user-friendly experience.

🚀 How It Works
Upload Your File: Choose a CSV, Excel, or PDF file from your local machine.

Data/Text Extraction:

For CSV and Excel, the app reads the data directly into a pandas DataFrame.

For PDF, pdfplumber extracts all readable text content (or tables if present and clearly structured) and provides it to the AI.

Ask a Question: Type your question about the file's content in plain English.

AI Analysis: The Gemini LLM receives your question along with a sample of your data (for CSV/Excel) or the extracted text (for PDF). It then analyzes the content.

Generate Insight & Chart: The AI generates a natural language response. If a visualization is appropriate for your question and the data allows, it will also provide structured chart specifications, which the app then renders using Altair.

🛠️ Setup and Installation
Follow these steps to get Project Insight up and running on your local machine.

Prerequisites
Python 3.8+

A Google Gemini API Key

1. Clone the Repository (if applicable)
If you have a Git repository, clone it:

git clone <your-repository-url>
cd <your-repository-name>

2. Create a Virtual Environment (Recommended)
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install Dependencies
Install all necessary Python packages:

pip install streamlit pandas google-generativeai python-dotenv openpyxl pdfplumber altair

openpyxl is needed for Excel file support.

pdfplumber is for PDF text/table extraction (does not require Java).

4. Configure Your Gemini API Key
Create a file named .env in the root directory of your project (the same directory as app.py). Add your Gemini API key to this file:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

Replace "YOUR_GEMINI_API_KEY" with your actual key from Google AI Studio.

5. Set Up Streamlit Configuration (Optional, for Theming)
For custom styling, create a folder named .streamlit in your project root, and inside it, create a file named config.toml with the following content:

.streamlit/config.toml

[theme]
primaryColor = "#6C63FF"          # A vibrant purple for primary actions/highlights
backgroundColor = "#F0F2F6"        # Light grey background
secondaryBackgroundColor = "#FFFFFF" # White for secondary elements like sidebars and containers
textColor = "#262626"              # Dark grey for general text for good readability
font = "sans serif"

🚀 Usage
Run the Streamlit App:

Make sure your virtual environment is active and you are in your project's root directory.

streamlit run app.py

This command will open the application in your web browser.

Upload a File:

Use the "Choose a file to begin analysis." uploader to select a CSV, Excel, or PDF document.

Ask a Question:

Type your question into the input box.

For tabular data (CSV/Excel): You can ask questions like "What is the average sales?", "Show me the distribution of categories?", "Plot Marks vs Attendance", or "Create a bar chart for branches."

For PDF documents (text-based): You can ask questions like "Summarize the document", "What are the key responsibilities mentioned?", or "Extract all dates from the document."

Get Insight:

Click the "Get Insight" button. The AI will process your request and display a textual explanation.

If a visualization is relevant and feasible (primarily for tabular data, experimental for text-based PDFs), a chart will be displayed above the text insight.

Clear Query:

Click "Clear Query" to reset the question input field.

💻 Technologies Used
Streamlit: For building the interactive web interface.

pandas: For data manipulation and reading various file formats.

Google Generative AI (google-generativeai): To access the Gemini LLM for AI analysis.

python-dotenv: For loading environment variables (API key).

openpyxl: For reading Excel files.

pdfplumber: For extracting text and tables from PDF documents.

altair: For declarative statistical visualizations.

💡 Future Enhancements (Ideas)
Advanced PDF Extraction: Implement more sophisticated PDF parsing for complex layouts or scanned documents (e.g., integrating OCR).

More Chart Types: Expand the range of supported chart types (e.g., pie charts, heatmaps).

Interactive Chart Customization: Allow users to modify chart parameters (e.g., axis labels, colors) directly
