import re

def normalize_text(text):
    """
    A utility function to clean and normalize a string for processing.

    This function performs the following operations:
    1. Converts the entire string to lowercase.
    2. Removes common punctuation to simplify text matching.
    3. Strips leading/trailing whitespace.
    4. Replaces multiple spaces with a single space.

    Args:
        text (str): The input string to normalize.

    Returns:
        str: The cleaned and normalized string.
    """
    if not isinstance(text, str):
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Replace multiple whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Example of how you might use this function:
if __name__ == '__main__':
    # This block will only run when you execute `python utils.py` directly
    # It's useful for testing your utility functions in isolation.
    
    original_text = "  This is a Test!! It has punctuation & numbers 123.  "
    normalized = normalize_text(original_text)
    
    print(f"Original: '{original_text}'")
    print(f"Normalized: '{normalized}'")

    # You could now update your other files to use this utility.
    # For example, in persona_analyzer.py, you could import it:
    # from utils import normalize_text
    # ...and then use normalize_text() instead of having a private _normalize_text method.

