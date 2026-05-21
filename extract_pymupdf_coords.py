import pymupdf
import unicodedata


def is_arabic(c):
    cp = ord(c)
    return (0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F or
            0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF)


def group_arabic_units(pairs):
    """
    pairs: list of (x, char) — Arabic base chars and diacritics, no spaces.
    Groups each diacritic with the base char at the same x (within 1.0 pt).
    Falls back to the nearest base char for unmatched diacritics.
    Returns list of (x, text) sorted by descending x (Arabic reading order).
    """
    bases = [(x, c) for x, c in pairs if not unicodedata.combining(c)]
    diacritics = [(x, c) for x, c in pairs if unicodedata.combining(c)]

    # Build units: list of [base_x, accumulated_text]
    units = [[x, c] for x, c in bases]

    for dx, d in diacritics:
        # Prefer exact x match (within floating-point noise)
        same = [(i, abs(u[0] - dx)) for i, u in enumerate(units) if abs(u[0] - dx) < 1.0]
        if same:
            i = min(same, key=lambda t: t[1])[0]
        elif units:
            i = min(range(len(units)), key=lambda i: abs(units[i][0] - dx))
        else:
            continue
        units[i][1] += d

    units.sort(key=lambda u: -u[0])  # descending x = Arabic reading order
    return "".join(text for _, text in units)


def build_runs(line_spans):
    """
    Iterates all chars in all spans of a line and groups them into directional
    runs: (is_rtl, [(x, char), ...]).

    Spaces between Arabic chars are dropped (PDF intra-word artifacts).
    Spaces adjacent to LTR text are kept with the LTR run.
    Diacritics (combining marks) are passed through and sorted later.
    """
    all_pairs = [(ch["origin"][0], ch["c"])
                 for span in line_spans
                 for ch in span["chars"]]

    # Peek helper: next non-space char after index i
    def next_nonspace(i):
        j = i + 1
        while j < len(all_pairs) and all_pairs[j][1].isspace():
            j += 1
        return all_pairs[j][1] if j < len(all_pairs) else None

    runs = []
    for i, (x, c) in enumerate(all_pairs):
        if c.isspace():
            nxt = next_nonspace(i)
            # Keep space only when it precedes LTR content
            if nxt is not None and not is_arabic(nxt) and not unicodedata.combining(nxt):
                if runs and not runs[-1][0]:
                    runs[-1][1].append((x, c))
                else:
                    runs.append([False, [(x, c)]])
            # Drop spaces before Arabic (intra-word artifacts) and trailing spaces
            continue

        if unicodedata.combining(c):
            # Diacritics: join current run (Arabic or LTR — resolved later)
            if runs:
                runs[-1][1].append((x, c))
            continue

        c_rtl = is_arabic(c)
        if runs and runs[-1][0] == c_rtl:
            runs[-1][1].append((x, c))
        else:
            runs.append([c_rtl, [(x, c)]])

    return runs


def reorder_bidi(runs, para_rtl):
    """
    runs: list of [is_rtl, [(x, char), ...]].
    Sorts chars within each run (Arabic: x-proximity grouping + desc sort;
    LTR: ascending x). Then sorts the runs by paragraph direction.
    Returns the final string.
    """
    result_parts = []
    run_refs = []  # (mean_x, text) for sorting runs

    for is_rtl, pairs in runs:
        if is_rtl:
            text = group_arabic_units(pairs)
        else:
            pairs_sorted = sorted(pairs, key=lambda t: t[0])
            text = "".join(c for _, c in pairs_sorted)

        mean_x = sum(x for x, _ in pairs) / len(pairs) if pairs else 0
        run_refs.append((mean_x, text))

    run_refs.sort(key=lambda t: -t[0] if para_rtl else t[0])
    return "".join(text for _, text in run_refs)


doc = pymupdf.open("arabic-book-sample.pdf")
pages_text = []

for page in doc:
    raw = page.get_text("rawdict")
    lines_text = []

    for block in raw["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            runs = build_runs(line["spans"])
            if not runs:
                continue
            para_rtl = line["dir"][0] < 0
            lines_text.append(reorder_bidi(runs, para_rtl))

    pages_text.append("\n".join(lines_text))

text = "\n\n".join(pages_text)

with open("arabic-book-sample-pymupdf-coords.txt", "w", encoding="utf-8") as f:
    f.write(text)
