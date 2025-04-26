from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from models import TextInput
from pipeline import segment_sentences
from embeddings import get_embeddings
from similarity import top_k_sentences
from amr_parser import parse_amr, amr_to_svg
from metrics import is_factually_consistent

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://amr-summarizer-prototype.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"message": "Pong!"}


@app.get("/")
def read_root():
    return {"message": "Hello from the AMR Summarizer API!"}


MAX_SUMMARY_LENGTH = 2000
MAX_ARTICLE_LENGTH = 10000


@app.post("/process_article", response_model=Dict)
def process_article(input_data: TextInput):
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

    # Simulate an error for testing purposes
    if (
        summary_clean.lower() == "simulate error"
        or article_clean.lower() == "simulate error"
    ):
        raise HTTPException(
            status_code=500, detail="Simulated backend error for testing."
        )

    sentences = segment_sentences(article_clean)
    if not sentences:
        raise HTTPException(
            status_code=400, detail="No valid sentences found in the article."
        )

    summary_embedding = get_embeddings([summary_clean])[0]
    sentence_embeddings = get_embeddings(sentences)
    top_sentences, scores = top_k_sentences(
        summary_embedding, sentence_embeddings, sentences, k=3
    )

    return {"top_sentences": top_sentences, "similarity_scores": scores}


@app.post("/process_amr", response_model=Dict)
def process_amr(input_data: TextInput):
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

    if (
        summary_clean.lower() == "simulate error"
        or article_clean.lower() == "simulate error"
    ):
        raise HTTPException(
            status_code=500, detail="Simulated backend error for testing."
        )

    sentences = segment_sentences(article_clean)
    if not sentences:
        raise HTTPException(
            status_code=400, detail="No valid sentences found in the article."
        )

    summary_embedding = get_embeddings([summary_clean])[0]
    sentence_embeddings = get_embeddings(sentences)
    top_sentences, _ = top_k_sentences(
        summary_embedding, sentence_embeddings, sentences, k=3
    )

    try:
        # Parse AMR graphs and convert to SVG
        summary_amr_raw = parse_amr(summary_clean)
        top_sentence_amrs_raw = {
            sentence: parse_amr(sentence) for sentence in top_sentences
        }
        summary_svg = amr_to_svg(summary_amr_raw)
        top_sentence_svgs = {
            sentence: amr_to_svg(amr) for sentence, amr in top_sentence_amrs_raw.items()
        }

        # Binary consistency check
        source_amrs = list(top_sentence_amrs_raw.values())
        is_consistent, consistency_score = is_factually_consistent(
            summary_amr_raw, source_amrs, threshold=0.8
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AMR parsing or visualization failed: {str(e)}"
        )

    return {
        "summary_svg": summary_svg,
        "top_sentence_svgs": top_sentence_svgs,
        "consistency_score": round(consistency_score, 3),
        "is_consistent": is_consistent,
    }
