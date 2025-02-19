from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import TextInput
from pipeline import segment_sentences

app = FastAPI()

# Configure CORS to allow your frontend to communicate with this backend.
origins = [
    "http://localhost:3000",  # or your React app URL/port
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/segment_sentences", response_model=List[str])
def segment_sentences_endpoint(input_data: TextInput):
    """
    Endpoint that segments the provided article text into sentences.
    Uses spaCy for sentence segmentation.
    
    Request Body:
      - summary: str (not used in segmentation here, but part of the TextInput model)
      - article: str
    
    Returns:
      - List of sentence strings.
    """
    sentences = segment_sentences(input_data.article)
    return sentences