import spacy

# Load the English model (ensure you have run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def segment_sentences(text: str):
    """
    Splits the input text into sentences using spaCy.
    
    Parameters:
        text (str): The text to segment.
    
    Returns:
        List[str]: A list of sentence strings.
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences
