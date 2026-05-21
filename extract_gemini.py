import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

pdf = genai.upload_file("arabic-book-sample.pdf", mime_type="application/pdf")
model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content([
    pdf,
    "Extract all text from this PDF exactly as it appears. "
    "Preserve all Arabic text with correct Unicode characters and reading order. "
    "Preserve document structure including headings, sections, and paragraphs."
])

with open("arabic-book-sample-gemini.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
