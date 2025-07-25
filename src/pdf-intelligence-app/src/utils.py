import spacy
import pytextrank

# Load a small spaCy model once. It will be downloaded during installation.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Add the pytextrank component to the spaCy pipeline.
nlp.add_pipe("textrank")
print("spaCy and pytextrank initialized successfully.")

def refine_text(text: str, num_sentences: int = 3) -> str:
    """
    Performs extractive summarization to get the most important sentences.
    """
    if not text or not isinstance(text, str):
        return ""
        
    doc = nlp(text)
    
    # Extract the top-ranked sentences to form a concise summary.
    refined_sentences = [sent.text for sent in doc._.textrank.summary(limit_phrases=15, limit_sentences=num_sentences)]
    
    return " ".join(refined_sentences)

def structure_content_from_headings(doc_path: str, headings: list) -> list:
    """
    A simple utility to convert the output of your PDFExtractor into
    a list of structured sections. This is a placeholder and can be
    made more sophisticated.
    """
    sections = []
    for heading in headings:
        sections.append({
            "document": doc_path,
            "page_number": heading.get("page", 1),
            "section_title": heading.get("text", "Untitled Section"),
            # NOTE: This is a placeholder. A more advanced version would
            # extract the actual text between this heading and the next.
            "text": f"This section is about {heading.get('text', '')}. The full text content would be extracted and placed here for analysis."
        })
    return sections
