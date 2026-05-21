import pymupdf
import unicodedata


def is_arabic(c):
    cp = ord(c)
    return (0x0600 <= cp <= 0x06FF or
            0x0750 <= cp <= 0x077F or
            0xFB50 <= cp <= 0xFDFF or
            0xFE70 <= cp <= 0xFEFF)


def fix_combining(chars):
    # Bubble combining marks (diacritics) to follow their base character
    result = list(chars)
    changed = True
    while changed:
        changed = False
        for i in range(len(result) - 1):
            if unicodedata.combining(result[i]) and not unicodedata.combining(result[i + 1]):
                result[i], result[i + 1] = result[i + 1], result[i]
                changed = True
    return result


doc = pymupdf.open("arabic-book-sample.pdf")
pages_text = []

for page in doc:
    raw = page.get_text("rawdict")
    lines_text = []

    for block in raw["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            chars = [(ch["origin"][0], ch["c"])
                     for span in line["spans"]
                     for ch in span["chars"]]

            if not chars:
                continue

            visible = [c for _, c in chars if not c.isspace()]
            arabic_ratio = (sum(1 for c in visible if is_arabic(c)) / len(visible)
                            if visible else 0)

            # RTL if line direction says so, or if mostly Arabic characters
            rtl = line["dir"][0] < 0 or arabic_ratio > 0.3
            chars.sort(key=lambda t: -t[0] if rtl else t[0])

            sorted_chars = fix_combining([c for _, c in chars])
            lines_text.append("".join(sorted_chars))

    pages_text.append("\n".join(lines_text))

text = "\n\n".join(pages_text)

with open("arabic-book-sample-pymupdf-coords.txt", "w", encoding="utf-8") as f:
    f.write(text)
