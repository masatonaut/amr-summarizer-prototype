from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from models import TextInput
from pipeline import segment_sentences  # Your spaCy segmentation function
from embeddings import get_embeddings
from similarity import top_k_sentences

app = FastAPI()

# Configure CORS for frontend access
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
    
    Request Body (TextInput):
      - summary: str
      - article: str
    
    Returns:
      Dict with keys:
        - "top_sentences": List of top 3 sentences.
        - "similarity_scores": Their corresponding cosine similarity scores.
    """
    # Step 1: Segment the article into sentences
    sentences = segment_sentences(input_data.article)
    
    if not sentences:
        return {"error": "No sentences found in the article."}
    
    # Step 2: Compute embeddings for the summary and for each sentence
    summary_embedding = get_embeddings([input_data.summary])[0]
    sentence_embeddings = get_embeddings(sentences)
    
    # Step 3: Select the top 3 sentences based on cosine similarity
    top_sentences, scores = top_k_sentences(summary_embedding, sentence_embeddings, sentences, k=3)
    
    return {
        "top_sentences": top_sentences,
        "similarity_scores": scores
    }
