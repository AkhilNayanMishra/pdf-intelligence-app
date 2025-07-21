import fitz  # PyMuPDF
import re
import joblib
import os
import numpy as np

class PDFExtractor:
    """
    Extracts the title and a hierarchical list of headings from a PDF file
    using a pre-trained machine learning model to classify text lines.
    """

    def __init__(self, pdf_path, model_path='src/heading_classifier.joblib'):
        """
        Initializes the extractor, opens the PDF, and loads the trained model.
        """
        self.pdf_path = pdf_path
        self.doc = None
        self.model = None

        # Open the PDF file
        try:
            self.doc = fitz.open(pdf_path)
        except fitz.errors.FileNotFoundError:
            print(f"Error: The file '{pdf_path}' was not found.")
            return

        # Load the pre-trained classifier model
        try:
            self.model = joblib.load(model_path)
        except FileNotFoundError:
            print(f"Error: Model file not found at '{model_path}'.")
            print("Please run the training script to create the model file.")
            return

    def _extract_features(self, page, line):
        """
        Extracts numerical features from a line of text for the model to use.
        """
        if not line['spans']:
            return None

        span = line['spans'][0]
        font_size = round(span['size'])
        is_bold = 1 if "bold" in span['font'].lower() else 0
        
        # Normalize vertical position (y-coordinate) by page height
        y_position = line['bbox'][1] / page.rect.height
        
        text = " ".join(s['text'] for s in line['spans']).strip()
        word_count = len(text.split())
        
        # Feature vector
        return [font_size, is_bold, y_position, word_count]

    def extract_structure(self):
        """
        Main method to extract structure using the trained model.
        """
        if not self.doc or not self.model:
            return "No Title Found", []

        headings = []
        all_lines_features = []
        line_references = []
        
        # First, extract features from all lines in the document
        for pnum, page in enumerate(self.doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0: # Text block
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

        # Use the trained model to predict which lines are headings
        predictions = self.model.predict(np.array(all_lines_features))
        
        # Filter for the lines that were predicted as headings (prediction == 1)
        for i, prediction in enumerate(predictions):
            if prediction == 1:
                # A simple rule for heading levels based on font size
                font_size_feature = all_lines_features[i][0]
                level = "H1" if font_size_feature > 15 else "H2" if font_size_feature > 12 else "H3"
                
                headings.append({
                    "level": level,
                    "text": line_references[i]['text'],
                    "page": line_references[i]['page']
                })
        
        # Assume the first heading found is the title
        title = headings[0]['text'] if headings else "No Title Found"
        
        return title, headings

