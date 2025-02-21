from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from models import TextInput
from pipeline import segment_sentences
from embeddings import get_embeddings
from similarity import top_k_sentences
from amr_parser import parse_amr  # Import the AMR parsing function

app = FastAPI()

# Configure CORS to allow access from your frontend.
origins = [
    "http://localhost:3000",
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    sentences = segment_sentences(input_data.article)
    if not sentences:
        return {"error": "No sentences found in the article."}
    
    summary_embedding = get_embeddings([input_data.summary])[0]
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
    # Step 1: Segment the article
    sentences = segment_sentences(input_data.article)
    if not sentences:
        return {"error": "No sentences found in the article."}
    
    # Step 2: Compute embeddings and select top sentences
    summary_embedding = get_embeddings([input_data.summary])[0]
    sentence_embeddings = get_embeddings(sentences)
    top_sentences, _ = top_k_sentences(summary_embedding, sentence_embeddings, sentences, k=3)
    
    # Step 3: Parse AMR for the summary and each top sentence
    summary_amr = parse_amr(input_data.summary)
    top_sentence_amrs = {sentence: parse_amr(sentence) for sentence in top_sentences}
    
    return {
        "summary_amr": summary_amr,
        "top_sentence_amrs": top_sentence_amrs
    }
