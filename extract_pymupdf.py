import pymupdf  # PyMuPDF

doc = pymupdf.open("arabic-book-sample.pdf")
text = "\n".join(page.get_text() for page in doc)

with open("arabic-book-sample-pymupdf.txt", "w", encoding="utf-8") as f:
    f.write(text)
