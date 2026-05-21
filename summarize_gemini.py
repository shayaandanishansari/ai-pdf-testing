import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

with open("arabic-book-sample.pdf", "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode()

response = httpx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
    params={"key": api_key},
    json={
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}},
                {"text": (
                    "Provide a comprehensive summary of this PDF. "
                    "Include the main topics covered, key concepts, and the overall purpose of the document."
                )}
            ]
        }]
    },
    timeout=120.0
)

text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

with open("arabic-book-sample-gemini-summary.txt", "w", encoding="utf-8") as f:
    f.write(text)
