import re

def normalize_text(text):
    if not isinstance(text, str):
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Replace multiple whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


if __name__ == '__main__':
   
    
    original_text = "  This is a Test!! It has punctuation & numbers 123.  "
    normalized = normalize_text(original_text)
    
    print(f"Original: '{original_text}'")
    print(f"Normalized: '{normalized}'")
