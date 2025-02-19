from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import TextInput

app = FastAPI()

# Allowed origins for CORS
origins = [
    "http://localhost:3001",
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_text")
def process_text(input_data: TextInput):
    return {
        "received_summary": input_data.summary,
        "received_article": input_data.article
    }
