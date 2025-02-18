from fastapi import FastAPI
from models import TextInput  # Import the model from models.py

app = FastAPI()

@app.post("/process_text")
def process_text(input_data: TextInput):
    # For now, simply echo the received data for testing purposes.
    return {
        "received_summary": input_data.summary,
        "received_article": input_data.article
    }

