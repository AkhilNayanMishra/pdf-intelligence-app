import re
from collections import Counter

class PersonaAnalyzer:
    """
    Analyzes structured document outlines to find and rank sections and subsections
    relevant to a given persona and their job-to-be-done.
    """

    def __init__(self, persona, job_to_be_done):
        """
        Initializes the analyzer with the persona and job context.

        Args:
            persona (str): Description of the user type (e.g. "Travel Planner").
            job_to_be_done (str): What the user is trying to accomplish.
        """
        if not persona or not job_to_be_done:
            raise ValueError("Persona and job_to_be_done cannot be empty.")
        self.persona = persona
        self.job_to_be_done = job_to_be_done
        self.keywords = self._extract_keywords()

    def _extract_keywords(self):
        stop_words = {
            'a', 'an', 'the', 'and', 'in', 'on', 'for', 'to', 'of', 'is', 'it', 'are',
            'i', 'me', 'my', 'you', 'your', 'he', 'she', 'we', 'our', 'they', 'their',
            'with', 'as', 'by', 'at', 'from', 'what', 'who', 'when', 'where', 'why',
            'how', 'be', 'will', 'has', 'had', 'do', 'does', 'did', 'can', 'could',
            'should', 'would', 'must', 'may', 'might', 'some', 'any', 'all', 'each',
            'other', 'about', 'after', 'before', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'this', 'that', 'these', 'those', 'am'
        }

        job_words = re.findall(r'\w+', self.job_to_be_done.lower())
        persona_words = re.findall(r'\w+', self.persona.lower())

        kws = Counter()
        for w in job_words:
            if w not in stop_words and len(w) > 2:
                kws[w] += 3
        for w in persona_words:
            if w not in stop_words and len(w) > 2:
                kws[w] += 1
        return kws

    def analyze_documents(self, document_outlines):
        """
        Finds and ranks relevant sections in a set of document outlines.

        Args:
            document_outlines (list of dict): Each dict must have 'outline' (list of headings)
                                              and optionally 'source_file'.

        Returns:
            tuple:
              - extracted_sections (list of dict): Ranked by relevance_score.
              - subsection_analysis (list of dict): Top 5 with refined_text.
        """
        scored = []
        for doc in document_outlines:
            if not doc.get('outline'):
                continue
            src = doc.get('source_file', 'Unknown')
            for heading in doc['outline']:
                text = heading['text']
                words = re.findall(r'\w+', text.lower())
                score = sum(self.keywords.get(w, 0) for w in words)

                # Boost cards: include culinary, cuisine, nightlife, entertainment
                if re.search(
                    r'guide|things to do|tips|tricks|how to|adventures'
                    r'|restaurants|hotels|cities'
                    r'|cuisine|culinary|nightlife|entertainment',
                    text,
                    re.IGNORECASE
                ):
                    score += 5

                if score > 0:
                    scored.append({
                        "document": src,
                        "page_number": heading['page'],
                        "section_title": text,
                        "relevance_score": score,
                        "refined_text": heading.get('subsection_text', '')
                    })

        # Sort by score descending
        ranked = sorted(scored, key=lambda x: x['relevance_score'], reverse=True)

        extracted_sections = []
        subsection_analysis = []
        for i, sec in enumerate(ranked):
            extracted_sections.append({
                "document": sec["document"],
                "section_title": sec["section_title"],
                "importance_rank": i + 1,
                "page_number": sec["page_number"]
            })
            if i < 5 and sec["refined_text"]:
                subsection_analysis.append({
                    "document": sec["document"],
                    "refined_text": sec["refined_text"],
                    "page_number": sec["page_number"]
                })

        return extracted_sections, subsection_analysis
