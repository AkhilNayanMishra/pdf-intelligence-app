import os
import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any

# --- PDF Processing Utility ---
# This function extracts the full text from a PDF file.

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a given PDF file using PyMuPDF.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
        return full_text
    except Exception as e:
        print(f"Could not read {os.path.basename(pdf_path)}: {e}")
        return ""

# --- Engine 1: Upgraded Semantic Relevance Engine ---
# This engine understands the *meaning* and *intent* behind your query.

class SemanticEngine:
    """
    Ranks documents based on semantic meaning using a powerful transformer model.
    """
    def __init__(self, model_name: str = 'multi-qa-mpnet-base-dot-v1'):
        """
        Initializes the engine and loads a sentence-transformer model optimized
        for semantic search and question answering.
        """
        print("Initializing Semantic Engine...")
        self.model = SentenceTransformer(model_name)
        print("Semantic Engine initialized successfully.")

    def rank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks documents by their semantic relevance to the query.
        """
        # This is the core of the semantic search. The model converts text into
        # vectors that represent its meaning.
        query_embedding = self.model.encode([query])
        doc_texts = [doc.get('text', '') for doc in documents]
        doc_embeddings = self.model.encode(doc_texts)
        
        # Cosine similarity measures how similar the query's meaning is to each document's meaning.
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

        for i, doc in enumerate(documents):
            doc['relevance_score'] = round(float(similarities[i]), 4)
        
        return sorted(documents, key=lambda x: x['relevance_score'], reverse=True)

# --- Engine 2: Classic Keyword Relevance Engine ---
# This engine ranks documents based on matching keywords (TF-IDF).

class KeywordEngine:
    """
    Ranks documents based on keyword frequency using Scikit-learn's TF-IDF.
    """
    def __init__(self):
        """
        Initializes the TF-IDF vectorizer from Scikit-learn.
        """
        print("\nInitializing Keyword Engine (TF-IDF)...")
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        print("Keyword Engine initialized successfully.")

    def rank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks documents by their keyword relevance to the query.
        """
        doc_texts = [doc.get('text', '') for doc in documents]
        
        # Learn the vocabulary and IDF from all documents, then create vectors.
        doc_vectors = self.vectorizer.fit_transform(doc_texts)
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity between the keyword vectors.
        similarities = cosine_similarity(query_vector, doc_vectors)[0]

        for i, doc in enumerate(documents):
            doc['relevance_score'] = round(float(similarities[i]), 4)
        
        return sorted(documents, key=lambda x: x['relevance_score'], reverse=True)

# --- Main Orchestrator ---

def analyze_and_rank_pdfs(input_dir: str, persona: str, job_to_be_done: str):
    """
    Analyzes PDFs using both semantic and keyword engines and prints the results.
    """
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{os.path.abspath(input_dir)}'")
        return

    print(f"Found {len(pdf_files)} PDFs to analyze...")
    documents = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        if text:
            documents.append({'filename': pdf_file, 'text': text})

    if not documents:
        print("Could not extract text from any PDFs. Aborting.")
        return

    query = f"As a {persona}, my goal is to {job_to_be_done}."
    print(f"\nFormulated AI Query: {query}")

    # --- Run Semantic Analysis ---
    semantic_engine = SemanticEngine()
    ranked_semantic = semantic_engine.rank(query, [d.copy() for d in documents])
    print("\n---Semantic Ranking Results (Correct Method) ---")
    print("This method understands context and should provide the most accurate ranking.")
    for i, doc in enumerate(ranked_semantic, 1):
        print(f"Rank #{i}: {doc['filename']} (Score: {doc['relevance_score']})")

    # --- Run Keyword Analysis ---
    keyword_engine = KeywordEngine()
    ranked_keyword = keyword_engine.rank(query, [d.copy() for d in documents])
    print("\n--- Classic Keyword Ranking Results (For Comparison) ---")
    print("This method matches keywords like 'dinner' or 'main course'.")
    for i, doc in enumerate(ranked_keyword, 1):
        print(f"Rank #{i}: {doc['filename']} (Score: {doc['relevance_score']})")


if __name__ == "__main__":
    PDF_INPUT_DIRECTORY = 'input'
    
    USER_PERSONA = "A family cook"
    JOB_TO_BE_DONE = "plan a hearty and impressive main course for a family dinner."

    if not os.path.exists(PDF_INPUT_DIRECTORY):
        print(f"Error: The input directory '{PDF_INPUT_DIRECTORY}' does not exist.")
        print("Please create it and place your PDF files inside.")
    else:
        analyze_and_rank_pdfs(PDF_INPUT_DIRECTORY, USER_PERSONA, JOB_TO_BE_DONE)
class RelevanceEngine:
    """
    Wrapper that uses SemanticEngine to rank document sections.
    """
    def __init__(self):
        self.semantic_engine = SemanticEngine()

    def rank_documents(self, persona, job_to_be_done, sections):
        query = f"As a {persona}, my goal is to {job_to_be_done}."
        # Each section should have a 'text' field
        ranked = self.semantic_engine.rank(query, [s.copy() for s in sections])
        # Add importance_rank for output
        for i, sec in enumerate(ranked, 1):
            sec['importance_rank'] = i
        return ranked