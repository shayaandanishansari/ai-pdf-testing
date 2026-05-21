import pdfplumber

with pdfplumber.open("arabic-book-sample.pdf") as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)

with open("arabic-book-sample-pdfplumber.txt", "w", encoding="utf-8") as f:
    f.write(text)
