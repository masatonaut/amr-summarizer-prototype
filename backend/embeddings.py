from sentence_transformers import SentenceTransformer

# Load the pre-trained model (this may download the model on first run)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(sentences):
    """
    Compute embeddings for a list of sentences.

    Parameters:
        sentences (List[str]): A list of sentence strings.

    Returns:
        numpy.ndarray: An array of embeddings.
    """
    embeddings = model.encode(sentences)
    return embeddings
