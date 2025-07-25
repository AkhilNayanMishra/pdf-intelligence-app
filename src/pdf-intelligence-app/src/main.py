import os
import datetime
from typing import List, Dict, Any

from src.pdf_extractor import PDFExtractor 
from src.persona_analyzer import RelevanceEngine
from src.utils import refine_text, structure_content_from_headings

def run_analysis_pipeline(doc_paths: List[str], persona: str, job_to_be_done: str) -> Dict[str, Any]:
    """
    Executes the full document intelligence pipeline.
    """
    print("--- Starting Persona-Driven Document Analysis ---")
    
    # --- 1. Document Structuring ---
    all_sections = []
    for doc_path in doc_paths:
        if not os.path.exists(doc_path):
            print(f"Warning: Document not found at {doc_path}. Skipping.")
            continue
        
        print(f"Parsing document: {doc_path}")
        # Use your existing PDFExtractor to get the document's structure.
        extractor = PDFExtractor(doc_path) 
        title, headings = extractor.extract_structure()
        
        # Convert the extracted headings into a list of structured sections.
        # This helper function can be improved to extract full paragraph text.
        all_sections.extend(structure_content_from_headings(doc_path, headings))

    if not all_sections:
        print("Could not extract any sections from the documents. Aborting.")
        return {}

    # --- 2. Relevance Ranking ---
    engine = RelevanceEngine()
    ranked_sections = engine.rank_documents(persona, job_to_be_done, all_sections)
    
    # --- 3. Sub-section Analysis & Refinement ---
    extracted_sections_output = []
    subsection_analysis_output = []
    
    top_n = min(5, len(ranked_sections))
    print(f"Refining the top {top_n} most relevant sections...")

    for section in ranked_sections[:top_n]:
        extracted_sections_output.append({
            "document": os.path.basename(section["document"]),
            "page_number": section["page_number"],
            "section_title": section["section_title"],
            "importance_rank": section["importance_rank"]
        })

        # Generate the 'Refined Text' for the sub-section analysis.
        refined = refine_text(section["text"])
        
        subsection_analysis_output.append({
            "document": os.path.basename(section["document"]),
            "page_number": section["page_number"],
            "refined_text": refined
        })

    # --- 4. Final Output Generation ---
    final_output = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in doc_paths],
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_section": extracted_sections_output,
        "sub-section_analysis": subsection_analysis_output
    }
    
    print("--- Analysis Complete ---")
    return final_output
