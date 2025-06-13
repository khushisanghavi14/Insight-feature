import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Choose an available Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Load the CSV dataset
df = pd.read_csv("employee_salary.csv")

# Convert DataFrame to string (limited to first few rows for performance)
data_string = df.head(20).to_csv(index=False)

# Ask a question
question = "What is the average salary in this dataset?"

# Combine the data and the question into a prompt
prompt = f"Here is a sample of the dataset:\n{data_string}\n\nNow, {question}"

# Generate response
response = model.generate_content(prompt)
print("Answer:", response.text)
