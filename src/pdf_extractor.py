import fitz  # PyMuPDF
import re
from collections import Counter

class PDFExtractor:
    """
    A sophisticated PDF extractor that identifies titles and hierarchical headings
    by analyzing font styles, text position, and structural keywords.
    """

    def __init__(self, pdf_path):
        """
        Initializes the PDFExtractor with the path to the PDF file.

        Args:
            pdf_path (str): The file path of the PDF document.
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_title_and_headings(self):
        """
        Extracts the title and a structured outline of headings from the PDF.

        Returns:
            tuple: A tuple containing the title (str) and the outline (list of dicts).
                   Returns (None, []) if the document is empty.
        """
        if not self.doc or self.doc.page_count == 0:
            return None, []

        all_blocks = self._get_all_text_blocks()
        if not all_blocks:
            return "", []

        styles = self._analyze_font_styles(all_blocks)
        title = self._extract_title(all_blocks[0], styles)
        headings = self._extract_headings(all_blocks, styles, title)
        return title, headings

    def _get_all_text_blocks(self):
        pages_blocks = []
        for page in self.doc:
            pages_blocks.append(page.get_text("dict")["blocks"])
        return pages_blocks

    def _analyze_font_styles(self, all_blocks):
        font_counts = Counter()
        for page_blocks in all_blocks:
            for block in page_blocks:
                if block['type'] != 0:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        size = round(span['size'])
                        font_counts[size] += len(span['text'].strip())
        if not font_counts:
            return []

        body_size = font_counts.most_common(1)[0][0]
        heading_sizes = sorted([s for s in font_counts if s > body_size], reverse=True)
        if not heading_sizes:
            heading_sizes = sorted(font_counts.keys(), reverse=True)
        return heading_sizes

    def _extract_title(self, first_page_blocks, styles):
        if not styles:
            return ""
        title_size = styles[0]
        candidates = []
        for block in first_page_blocks:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                if any(round(span['size']) == title_size for span in line['spans']):
                    text = " ".join(span['text'] for span in line['spans']).strip()
                    if text:
                        candidates.append((block['bbox'][1], text))
        candidates.sort()
        return " ".join(t for _, t in candidates).replace("  ", " ").strip()

    def _extract_headings(self, all_blocks, styles, title):
        if not styles:
            return []
        level_map = {size: f"H{i+1}" for i, size in enumerate(styles)}
        headings = []

        for pnum, page_blocks in enumerate(all_blocks, start=1):
            for block in page_blocks:
                if block['type'] != 0:
                    continue
                for line in block['lines']:
                    text = " ".join(s['text'] for s in line['spans']).strip()
                    if not text or len(text) < 3 or (title and text in title):
                        continue

                    match = re.match(r'^(\d+(\.\d+)*\.?|\w\.|Appendix\s\w:)\s+', text)
                    size = round(line['spans'][0]['size'])
                    level = None

                    if match:
                        prefix = match.group(1)
                        depth = prefix.count('.') + 1
                        level = 'H1' if 'Appendix' in prefix else f"H{depth}"
                    elif size in level_map:
                        level = level_map[size]

                    if level and not (text.endswith('.') and not match):
                        headings.append({
                            "level": level,
                            "text": text,
                            "page": pnum
                        })

        # Deduplicate
        unique, seen = [], set()
        for h in headings:
            key = (h['text'], h['level'])
            if key not in seen:
                unique.append(h)
                seen.add(key)
        return unique
