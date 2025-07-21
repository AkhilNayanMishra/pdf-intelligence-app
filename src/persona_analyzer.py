import re
from collections import Counter

class PersonaAnalyzer:
    """
    Analyzes structured document outlines to find and rank sections and subsections
    relevant to a given persona and their job-to-be-done.
    """

    def __init__(self, persona, job_to_be_done):
        """Initializes the analyzer with the persona and job context."""
        if not persona or not job_to_be_done:
            raise ValueError("Persona and job_to_be_done cannot be empty.")
            
        self.persona = persona
        self.job_to_be_done = job_to_be_done
        self.keywords = self._extract_keywords()

    def _extract_keywords(self):
        """
        Extracts and weights keywords from the persona and job description.
        Keywords from the job description are given higher importance.
        """
        stop_words = {
            'a', 'an', 'the', 'and', 'in', 'on', 'for', 'to', 'of', 'is', 'it', 'are', 's',
            'i', 'me', 'my', 'you', 'your', 'he', 'she', 'we', 'our', 'they', 'their', 
            'with', 'as', 'by', 'at', 'from', 'what', 'who', 'when', 'where', 'why', 
            'how', 'be', 'will', 'has', 'had', 'do', 'does', 'did', 'can', 'could',
            'should', 'would', 'must', 'may', 'might', 'some', 'any', 'all', 'each',
            'other', 'about', 'after', 'before', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'this', 'that', 'these', 'those', 'am'
        }
        
        job_words = re.findall(r'\w+', self.job_to_be_done.lower())
        persona_words = re.findall(r'\w+', self.persona.lower())
        
        keywords = Counter()
        for word in job_words:
            if word not in stop_words and len(word) > 2:
                keywords[word] += 3
        
        for word in persona_words:
            if word not in stop_words and len(word) > 2:
                keywords[word] += 1
        
        return keywords

    def analyze_documents(self, document_outlines):
        """
        Analyzes a collection of structured outlines to find and rank relevant sections.
        """
        scored_sections = []

        for doc in document_outlines:
            if 'outline' not in doc or not doc['outline']:
                continue

            for heading in doc['outline']:
                # Start with a base score of 1 for every heading.
                score = 1
                heading_text_lower = heading['text'].lower()
                heading_words = re.findall(r'\w+', heading_text_lower)
                
                # Score based on keyword matches in the heading text
                for word in heading_words:
                    if word in self.keywords:
                        score += self.keywords[word]
                
                # Boost score for a wider range of relevant terms
                boost_terms = [
                    'breakfast', 'lunch', 'dinner', 'ideas', 'mains', 'sides', 'recipe', 
                    'meals', 'healthy', 'family', 'plan', 'guide', 'things to do', 'tips', 
                    'tricks', 'how to', 'adventures', 'restaurants', 'hotels', 'cities', 
                    'cuisine', 'coastal', 'packing', 'features', 'creating', 'editing', 'sharing'
                ]
                for term in boost_terms:
                    if term in heading_text_lower:
                        score += 5

                # **IMPROVEMENT**: We will now always add the section to be ranked.
                # The sorting later will handle prioritizing the best ones.
                scored_sections.append({
                    "document": doc.get('source_file', 'Unknown'),
                    "page_number": heading['page'],
                    "section_title": heading['text'],
                    "relevance_score": score,
                    "refined_text": heading.get('subsection_text', '')
                })

        # Sort by relevance score
        ranked_sections = sorted(scored_sections, key=lambda x: x['relevance_score'], reverse=True)

        # Prepare the final output lists
        extracted_sections_output = []
        subsection_analysis_output = []

        for i, section in enumerate(ranked_sections):
            extracted_sections_output.append({
                "document": section["document"],
                "section_title": section["section_title"],
                "importance_rank": i + 1,
                "page_number": section["page_number"]
            })
            
            if i < 5 and section["refined_text"]:
                 subsection_analysis_output.append({
                    "document": section["document"],
                    "refined_text": section["refined_text"],
                    "page_number": section["page_number"]
                })

        return extracted_sections_output, subsection_analysis_output
