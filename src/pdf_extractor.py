# pdf_extractor.py
import fitz  # PyMuPDF

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_title_and_headings(self):
        doc = fitz.open(self.pdf_path)
        headings = []
        title_text = ""

        # 1) Gather all distinct font sizes (descending)
        font_sizes = set()
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            font_sizes.add(span["size"])
        font_sizes = sorted(font_sizes, reverse=True)

        # 2) Map largest fonts → H1, next → H2, then H3, H4
        level_map = {}
        levels = ["H1", "H2", "H3", "H4"]
        for i, size in enumerate(font_sizes[:4]):
            level_map[size] = levels[i]

        # 3) Walk pages again, pick only centered, colon‐containing, non‐bulleted lines
        for page_num, page in enumerate(doc, start=1):
            page_mid = page.rect.width / 2

            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block or "bbox" not in block:
                    continue

                # compute block center
                x0, y0, x1, y1 = block["bbox"]
                block_center = (x0 + x1) / 2
                is_centered = abs(block_center - page_mid) < (page.rect.width * 0.2)

                if not is_centered:
                    continue

                for line in block["lines"]:
                    # join all spans into one line
                    text = " ".join(span["text"].strip() for span in line["spans"]).strip()
                    if len(text) < 3:
                        continue
                    if ":" not in text:
                        continue
                    if text[0] in ("•", "-", "*"):
                        continue

                    # font size of this line (use first span)
                    size = line["spans"][0]["size"]
                    level = level_map.get(size)
                    if not level:
                        continue

                    # first H1 with colon is the title
                    if level == "H1" and not title_text:
                        title_text = text

                    headings.append({
                        "level": level,
                        "text": text,
                        "page": page_num
                    })

        return title_text, headings
