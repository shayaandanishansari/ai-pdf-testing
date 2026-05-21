import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

pdf = genai.upload_file("arabic-book-sample.pdf", mime_type="application/pdf")
model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content([
    pdf,
    "Provide a comprehensive summary of this PDF. "
    "Include the main topics covered, key concepts, and the overall purpose of the document."
])

with open("arabic-book-sample-gemini-summary.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
