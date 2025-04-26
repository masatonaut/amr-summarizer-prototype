import numpy as np
from numpy.linalg import norm


def cosine_similarity(vector1, vector2):
    """
    Compute cosine similarity between two vectors.

    Parameters:
        vector1 (numpy.ndarray): First vector.
        vector2 (numpy.ndarray): Second vector.

    Returns:
        float: Cosine similarity.
    """
    return np.dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def top_k_sentences(summary_embedding, sentence_embeddings, sentences, k=3):
    """
    Select the top k sentences most similar to the summary.

    Parameters:
        summary_embedding (numpy.ndarray): Embedding of the summary.
        sentence_embeddings (numpy.ndarray): Embeddings of each sentence.
        sentences (List[str]): Original sentences.
        k (int): Number of top sentences to return.

    Returns:
        Tuple[List[str], List[float]]: A tuple containing the list of top k sentences
        and their corresponding similarity scores as native floats.
    """
    similarities = [
        cosine_similarity(summary_embedding, sent_emb)
        for sent_emb in sentence_embeddings
    ]
    # Get the indices of the top k scores
    top_indices = np.argsort(similarities)[-k:][::-1]
    top_sentences = [sentences[i] for i in top_indices]
    # Convert the similarity scores to native Python floats
    top_scores = [float(similarities[i]) for i in top_indices]
    return top_sentences, top_scores
