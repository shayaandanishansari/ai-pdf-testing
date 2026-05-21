import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

with open("arabic-book-sample.pdf", "rb") as f:
    file_obj = client.files.create(file=f, purpose="file-extract")

response = client.chat.completions.create(
    model="qwen-long",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (
            f"fileid://{file_obj.id}\n\n"
            "Provide a comprehensive summary of this PDF. "
            "Include the main topics covered, key concepts, and the overall purpose of the document."
        )}
    ]
)

with open("arabic-book-sample-qwen-summary.txt", "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content)
