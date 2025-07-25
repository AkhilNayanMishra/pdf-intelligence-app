import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import fitz  # PyMuPDF

def _extract_features(page, line):
    """
    Extracts numerical features from a line of text.
    NOW INCLUDES an 'is_centered' feature.
    """
    if not line['spans']:
        return None

    span = line['spans'][0]
    text = " ".join(s['text'] for s in line['spans']).strip()

    # --- Feature Engineering ---
    font_size = round(span['size'])
    is_bold = 1 if "bold" in span['font'].lower() else 0
    y_position = line['bbox'][1] / page.rect.height if page.rect.height > 0 else 0
    word_count = len(text.split())
    is_all_caps = 1 if text.isupper() and len(text) > 3 else 0

    # --- NEW FEATURE: is_centered ---
    # Calculates if the line is horizontally centered on the page.
    page_width = page.rect.width
    line_center = (line['bbox'][0] + line['bbox'][2]) / 2
    page_center = page_width / 2
    # Consider it centered if it's within 5% of the page's center
    tolerance = page_width * 0.05
    is_centered = 1 if abs(line_center - page_center) < tolerance else 0

    return [font_size, is_bold, y_position, word_count, is_all_caps, is_centered]

def create_dataset_from_files(file_mapping, input_dir='.'):
    """
    Creates a multi-class dataset by parsing PDFs and using JSON files for labels.
    """
    print(f"Searching for input files in the following directory: '{os.path.abspath(input_dir)}'")
    print("Creating multi-class dataset from provided files...")

    dataset_for_csv = []
    all_features = []
    all_labels = []

    for pdf_filename, json_filename in file_mapping.items():
        pdf_path = os.path.join(input_dir, pdf_filename)
        json_path = os.path.join(input_dir, json_filename)

        if not os.path.exists(pdf_path) or not os.path.exists(json_path):
            print(f"  - ERROR: File not found at '{os.path.abspath(pdf_path)}' or '{os.path.abspath(json_path)}'. Skipping.")
            continue
        
        print(f"  - Processing: {pdf_filename}")
        with open(json_path, 'r', encoding='utf-8') as f:
            ground_truth = json.load(f)

        true_headings = {item['text'].strip(): item['level'] for item in ground_truth.get('outline', [])}
        if ground_truth.get('title'):
            true_headings[ground_truth['title'].strip()] = 'Title'
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"  - Error opening {pdf_filename}: {e}")
            continue

        for pnum, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        features = _extract_features(page, line)
                        if features:
                            text = " ".join(s['text'] for s in line['spans']).strip()
                            label = true_headings.get(text, 'Body_Text')
                            all_features.append(features)
                            all_labels.append(label)
                            dataset_for_csv.append([text] + features + [label])
        doc.close()

    print(f"Dataset creation complete. Found {len(all_features)} total text lines.")
    return np.array(all_features), np.array(all_labels), dataset_for_csv

def train_and_save_model():
    """
    Main function to create dataset, train classifier, and save it.
    """
    file_mapping = {
        "Dinner Ideas - Sides_1.pdf": "Dinner Ideas - Sides_1.json",
        "Dinner Ideas - Sides_2.pdf": "Dinner Ideas - Sides_2.json",
        "STEMPathwaysFlyer.pdf": "STEMPathwaysFlyer.json",
        "E0H1CM114.pdf": "E0H1CM114.json",
        "E0CCG5S239.pdf": "E0CCG5S239.json"
    }

    features, labels, csv_data = create_dataset_from_files(file_mapping, input_dir='input')

    if features.shape[0] == 0:
        print("\nCould not create a dataset. Aborting training.")
        return

    # UPDATED columns to include the new feature
    csv_columns = ['text', 'font_size', 'is_bold', 'y_position', 'word_count', 'is_all_caps', 'is_centered', 'label']
    df = pd.DataFrame(csv_data, columns=csv_columns)

    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, 'training_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nDataset saved to '{csv_path}'")

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.25, random_state=42, stratify=labels
    )
    print(f"\nDataset split into {len(X_train)} training samples and {len(X_test)} testing samples.")

    print("\nStarting model training with RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    print("Model training complete.")

    print("\nEvaluating model performance...")
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Overall Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    class_names = sorted(list(set(y_train) | set(y_test)))
    print(classification_report(y_test, predictions, labels=class_names, zero_division=0))

    src_dir = 'src'
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    model_filename = os.path.join(src_dir, 'heading_classifier.joblib')
    joblib.dump(model, model_filename)
    joblib.dump(model.classes_, os.path.join(src_dir, 'heading_model_classes.joblib'))
    print(f"\nModel and class names successfully saved to the '{src_dir}' directory.")

if __name__ == "__main__":
    train_and_save_model()