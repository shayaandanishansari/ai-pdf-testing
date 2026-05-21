import os
import base64
import httpx
import pymupdf
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("QWEN_API_KEY")

doc = pymupdf.open("arabic-book-sample.pdf")
pages = []
for page in doc:
    png = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).tobytes("png")
    pages.append(base64.b64encode(png).decode())

content = [
    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
    for b64 in pages
]
content.append({"type": "text", "text": (
    "Extract all text from these PDF pages exactly as it appears. "
    "Preserve all Arabic text with correct Unicode characters and reading order. "
    "Preserve document structure including headings, sections, and paragraphs."
)})

response = httpx.post(
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={
        "model": "qwen3.5-397b-a17b",
        "messages": [{"role": "user", "content": content}]
    },
    timeout=180.0
)

data = response.json()
if "choices" not in data:
    raise RuntimeError(data)

with open("arabic-book-sample-qwen.txt", "w", encoding="utf-8") as f:
    f.write(data["choices"][0]["message"]["content"])
