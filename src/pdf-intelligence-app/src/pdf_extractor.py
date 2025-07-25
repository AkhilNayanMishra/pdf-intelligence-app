import fitz  # PyMuPDF
import joblib
import os
import numpy as np

class PDFExtractor:
    """
    Extracts document structure using a pre-trained, multi-class
    machine learning model to classify text lines as Title, H1, H2, etc.
    """

    def __init__(self, pdf_path, model_path='src/heading_classifier.joblib', classes_path='src/heading_model_classes.joblib'):
        self.pdf_path = pdf_path
        self.doc = None
        self.model = None
        self.model_classes = None

        if not os.path.exists(pdf_path):
            print(f"Error: The file '{pdf_path}' was not found.")
            return
        
        try:
            self.doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening or processing PDF {pdf_path}: {e}")
            self.doc = None
            return

        try:
            self.model = joblib.load(model_path)
            self.model_classes = joblib.load(classes_path)
        except FileNotFoundError:
            print(f"Error: Model file not found at '{model_path}' or '{classes_path}'.")
            return

    def _extract_features(self, page, line):
        """
        Extracts numerical features from a line of text for prediction.
        NOW INCLUDES 'is_centered'.
        """
        if not line['spans']:
            return None

        span = line['spans'][0]
        
        # CORRECTED: This now extracts all 6 features to match the model
        font_size = round(span['size'])
        is_bold = 1 if "bold" in span['font'].lower() else 0
        y_position = line['bbox'][1] / page.rect.height if page.rect.height > 0 else 0
        word_count = len(" ".join(s['text'] for s in line['spans']).strip().split())
        is_all_caps = 1 if " ".join(s['text'] for s in line['spans']).strip().isupper() and len(" ".join(s['text'] for s in line['spans']).strip()) > 3 else 0

        # --- NEW FEATURE: is_centered ---
        page_width = page.rect.width
        line_center = (line['bbox'][0] + line['bbox'][2]) / 2
        page_center = page_width / 2
        tolerance = page_width * 0.05
        is_centered = 1 if abs(line_center - page_center) < tolerance else 0
        
        return [font_size, is_bold, y_position, word_count, is_all_caps, is_centered]

    def extract_structure(self):
        """
        Main method to extract structure using the trained multi-class model.
        """
        if not self.doc or self.model is None:
            return "No Title Found", []

        headings = []
        all_lines_features = []
        line_references = []
        
        for pnum, page in enumerate(self.doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        features = self._extract_features(page, line)
                        if features:
                            all_lines_features.append(features)
                            line_references.append({
                                'text': " ".join(s['text'] for s in line['spans']).strip(),
                                'page': pnum + 1
                            })
        
        if not all_lines_features:
            return "No Title Found", []

        predicted_class_names = self.model.predict(np.array(all_lines_features))
        
        title = "No Title Found"
        found_title = False
        for i, class_name in enumerate(predicted_class_names):
            if class_name == 'Title' and not found_title:
                title = line_references[i]['text']
                found_title = True
            
            if class_name != 'Body_Text':
                headings.append({
                    "level": class_name,
                    "text": line_references[i]['text'],
                    "page": line_references[i]['page']
                })
        
        if not found_title and headings:
            title = headings[0]['text']
        
        return title, headings