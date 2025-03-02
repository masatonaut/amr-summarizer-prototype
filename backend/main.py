from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Use relative imports so everything stays within the backend package
from .models import TextInput
from .pipeline import segment_sentences
from .embeddings import get_embeddings
from .similarity import top_k_sentences
from .amr_parser import parse_amr  # Import the AMR parsing function

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://amr-summarizer-prototype.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"message": "Pong!"}

@app.get("/")
def read_root():
    return {"message": "Hello from the AMR Summarizer API!"}

# Define maximum allowed lengths for input validation
MAX_SUMMARY_LENGTH = 2000
MAX_ARTICLE_LENGTH = 10000

@app.post("/process_article", response_model=Dict)
def process_article(input_data: TextInput):
    """
    Process an article by segmenting it into sentences, computing embeddings,
    and selecting the top 3 sentences most similar to the summary.

    Returns:
      A dictionary with:
        - "top_sentences": The selected top sentences.
        - "similarity_scores": Their corresponding cosine similarity scores.
    """
    # Trim whitespace and validate inputs
    summary_clean = input_data.summary.strip()
    article_clean = input_data.article.strip()

    if not summary_clean:
        raise HTTPException(status_code=400, detail="Summary is required.")
    if not article_clean:
        raise HTTPException(status_code=400, detail="Article is required.")
    if len(summary_clean) > MAX_SUMMARY_LENGTH:
        raise HTTPException(status_code=400, detail="Summary is too long.")
    if len(article_clean) > MAX_ARTICLE_LENGTH:
        raise HTTPException(status_code=400, detail="Article is too long.")

    # Simulate a backend error for testing purposes
    if summary_clean.lower() == "simulate error" or article_clean.lower() == "simulate error":
        raise HTTPException(status_code=500, detail="Simulated backend error for testing.")

    # Process the article
    sentences = segment_sentences(article_clean)
    if not sentences:
        raise HTTPException(status_code=400, detail="No valid sentences found in the article.")

    summary_embedding = get_embeddings([summary_clean])[0]
    sentence_embeddings = get_embeddings(sentences)
    top_sentences, scores = top_k_sentences(summary_embedding, sentence_embeddings, sentences, k=3)

    return {
        "top_sentences": top_sentences,
        "similarity_scores": scores
    }

@app.post("/process_amr", response_model=Dict)
def process_amr(input_data: TextInput):
    """
    Process text by generating AMR graphs for the summary and the top sentences.

    Workflow:
      1. Segment the article into sentences.
      2. Compute embeddings for the summary and sentences.
      3. Select the top 3 sentences based on cosine similarity.
      4. Parse AMR graphs for the summary and each top sentence.

    Returns:
      A dictionary with:
        - "summary_amr": The AMR graph for the summary.
        - "top_sentence_amrs": A dictionary mapping each top sentence to its AMR graph.
    """
    # Trim whitespace and validate inputs
    summary_clean = input_data.summary.strip()
    article_clean = input_data.article.strip()

    if not summary_clean:
        raise HTTPException(status_code=400, detail="Summary is required.")
    if not article_clean:
        raise HTTPException(status_code=400, detail="Article is required.")
    if len(summary_clean) > MAX_SUMMARY_LENGTH:
        raise HTTPException(status_code=400, detail="Summary is too long.")
    if len(article_clean) > MAX_ARTICLE_LENGTH:
        raise HTTPException(status_code=400, detail="Article is too long.")

    # Simulate a backend error for testing purposes
    if summary_clean.lower() == "simulate error" or article_clean.lower() == "simulate error":
        raise HTTPException(status_code=500, detail="Simulated backend error for testing.")

    # Step 1: Segment the article into sentences
    sentences = segment_sentences(article_clean)
    if not sentences:
        raise HTTPException(status_code=400, detail="No valid sentences found in the article.")

    # Step 2: Compute embeddings and select top sentences
    summary_embedding = get_embeddings([summary_clean])[0]
    sentence_embeddings = get_embeddings(sentences)
    top_sentences, _ = top_k_sentences(summary_embedding, sentence_embeddings, sentences, k=3)

    # Step 3: Parse AMR for the summary and each top sentence
    try:
        summary_amr = parse_amr(summary_clean)
        top_sentence_amrs = {sentence: parse_amr(sentence) for sentence in top_sentences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AMR parsing failed: {str(e)}")

    return {
        "summary_amr": summary_amr,
        "top_sentence_amrs": top_sentence_amrs
    }
