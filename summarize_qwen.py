import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("QWEN_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

with open("arabic-book-sample.pdf", "rb") as f:
    upload = httpx.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/files",
        headers=headers,
        files={"file": ("arabic-book-sample.pdf", f, "application/pdf")},
        data={"purpose": "file-extract"},
        timeout=60.0
    )
file_id = upload.json()["id"]

response = httpx.post(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={**headers, "Content-Type": "application/json"},
    json={
        "model": "qwen-long",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": (
                f"fileid://{file_id}\n\n"
                "Provide a comprehensive summary of this PDF. "
                "Include the main topics covered, key concepts, and the overall purpose of the document."
            )}
        ]
    },
    timeout=120.0
)

text = response.json()["choices"][0]["message"]["content"]

with open("arabic-book-sample-qwen-summary.txt", "w", encoding="utf-8") as f:
    f.write(text)
