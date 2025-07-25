import os
import json
from pdf_extractor import PDFExtractor # We use the extractor to make predictions

def generate_json_for_unlabeled_pdfs(pdf_files, input_dir='input'):
    """
    Uses the trained model inside PDFExtractor to predict the structure
    of new PDFs and save them as JSON files.
    """
    print("Starting label generation for new PDFs...")

    for pdf_filename in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_filename)
        if not os.path.exists(pdf_path):
            print(f"Warning: Could not find '{pdf_filename}'. Skipping.")
            continue

        print(f"  - Processing: {pdf_filename}")
        
        # Use the PDFExtractor to get the model's predictions
        extractor = PDFExtractor(pdf_path)
        title, headings = extractor.extract_structure()

        # Prepare the output in the same format as your other JSON files
        output_data = {
            "title": title,
            "outline": headings
        }

        # Save the new JSON file
        json_filename = os.path.splitext(pdf_filename)[0] + ".json"
        json_path = os.path.join(input_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)
            
        print(f"    -> Successfully created '{json_filename}'")

if __name__ == "__main__":
    # List of the new PDF files that need JSON labels
    new_pdfs = [
        "Lunch Ideas.pdf",
        "Dinner Ideas - Sides_1.pdf",
        "Dinner Ideas - Sides_2.pdf",
        "Dinner Ideas - Sides_3.pdf",
        "Dinner Ideas - Sides_4.pdf"
    ]
    
    generate_json_for_unlabeled_pdfs(new_pdfs)
    print("\nLabel generation complete.")
