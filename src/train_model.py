import os
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import fitz  # PyMuPDF

def _extract_features(page, line):
    """
    Extracts numerical features from a line of text. Now includes an 'is_all_caps' feature.
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
    # New feature: Check if the text is mostly uppercase (and not just a short acronym)
    is_all_caps = 1 if text.isupper() and len(text) > 3 else 0
    
    return [font_size, is_bold, y_position, word_count, is_all_caps]

def create_dataset_from_files(file_mapping, input_dir='input'):
    """
    Creates a multi-class dataset by parsing PDFs and using JSON files for labels.
    """
    print("Creating multi-class dataset from provided files...")
    
    all_features = []
    all_labels = [] # Will store string labels like "H1", "Body_Text", etc.

    for pdf_filename, json_filename in file_mapping.items():
        pdf_path = os.path.join(input_dir, pdf_filename)
        json_path = os.path.join(input_dir, json_filename)

        if not os.path.exists(pdf_path) or not os.path.exists(json_path):
            continue
            
        print(f"  - Processing: {pdf_filename}")

        with open(json_path, 'r', encoding='utf-8') as f:
            ground_truth = json.load(f)
        
        # Use a dictionary to map heading text to its level (e.g., "H1")
        true_headings = {item['text'].strip(): item['level'] for item in ground_truth.get('outline', [])}
        # Add the document title to this dictionary
        if ground_truth.get('title'):
            true_headings[ground_truth['title'].strip()] = 'Title'

        doc = fitz.open(pdf_path)
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        features = _extract_features(page, line)
                        if features:
                            text = " ".join(s['text'] for s in line['spans']).strip()
                            
                            # Get the specific label (e.g., "H1", "H2") from our dictionary
                            label = true_headings.get(text, 'Body_Text')
                            
                            all_features.append(features)
                            all_labels.append(label)
        doc.close()

    print(f"Dataset creation complete. Found {len(all_features)} total text lines.")
    return np.array(all_features), np.array(all_labels)

def train_and_save_model():
    """
    Main function to create the dataset, train the multi-class classifier, and save it.
    """
    file_mapping = {
        "E0H1CM114.pdf": "E0H1CM114.json",
        "E0CCG5S312.pdf": "E0CCG5S312.json",
        "E0CCG5S239.pdf": "E0CCG5S239.json",
        "STEMPathwaysFlyer.pdf": "STEMPathwaysFlyer.json",
        "TOPJUMP-PARTY-INVITATION-20161003-V01.pdf": "TOPJUMP-PARTY-INVITATION-20161003-V01.json"
    }

    features, labels = create_dataset_from_files(file_mapping)

    if features.shape[0] == 0:
        print("Could not create a dataset. Aborting training.")
        return

    # --- Split Data ---
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.25, random_state=42, stratify=labels
    )
    print(f"\nDataset split into {len(X_train)} training samples and {len(X_test)} testing samples.")

    # --- Train the Upgraded Model ---
    print("\nStarting model training with RandomForestClassifier...")
    # RandomForest is a more powerful model, great for multi-class problems.
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    print("Model training complete.")

    # --- Evaluate the Model ---
    print("\nEvaluating model performance...")
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Overall Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    # Ensure all possible labels are included in the report for clarity
    class_names = sorted(list(set(y_train) | set(y_test)))
    print(classification_report(y_test, predictions, labels=class_names))

    # --- Save the Final Model and its classes ---
    model_filename = 'src/heading_classifier.joblib'
    joblib.dump(model, model_filename)
    # Also save the class names, so the extractor knows what the model's outputs mean
    joblib.dump(model.classes_, 'src/heading_model_classes.joblib')
    print(f"Model and class names successfully saved.")

if __name__ == "__main__":
    train_and_save_model()
