import fitz  # PyMuPDF

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_title_and_headings(self):
        doc = fitz.open(self.pdf_path)
        headings = []
        title_candidates = []
        font_sizes_on_page1 = []

        # Step 1: Detect title from page 1 using max font size
        page1 = doc[0]
        blocks = page1.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font_sizes_on_page1.append(span["size"])

        if not font_sizes_on_page1:
            return "", []

        max_font = max(font_sizes_on_page1)

        # Step 2: Collect all spans with max font as title candidates
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = " ".join([
                    span["text"].strip()
                    for span in line["spans"]
                    if abs(span["size"] - max_font) < 0.5
                ])
                if line_text:
                    title_candidates.append(line_text)

        # Join them to form title
        title_text = "  ".join(title_candidates).strip()

        # Step 3: Extract headings from all pages
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    spans = line["spans"]
                    if not spans:
                        continue
                    font_size = spans[0]["size"]
                    text = " ".join([s["text"].strip() for s in spans]).strip()

                    if not text or len(text) < 4:
                        continue

                    # Skip lines with only symbols or too much uppercase noise
                    if (
                        all(c.isupper() or not c.isalpha() for c in text.replace(" ", ""))
                        and len(text) < 25
                    ):
                        continue

                    # Heading level logic
                    if font_size > 16:
                        level = "H1"
                    elif font_size > 13.5:
                        level = "H2"
                    elif font_size > 11:
                        level = "H3"
                    elif font_size > 9.5:
                        level = "H4"
                    else:
                        continue

                    # Avoid duplicating title
                    if any(text.lower() == t.lower() for t in title_candidates):
                        continue

                    headings.append({
                        "level": level,
                        "text": text,
                        "page": page_num + 1
                    })

        return title_text, headings
