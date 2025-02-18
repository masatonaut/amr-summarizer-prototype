# amr-summarizer-prototype

This repository contains a prototype project for generating and comparing Abstract Meaning Representation (AMR) graphs from summary and article texts.

## Overview

The project utilizes a FastAPI backend for processing text and generating AMR graphs, and a React frontend for the user interface. The prototype aims to reach approximately 70% completion by March 1, 2025.

## Components

- **Backend:**
  - **FastAPI & Uvicorn:** For building and serving API endpoints.
  - **NLP Libraries:** 
    - *spaCy* or *Stanza* for sentence segmentation.
    - *Sentence-BERT* (or a similar model) for computing sentence embeddings.
    - *amrlib* for AMR parsing.
  - **Additional Tools:** Pydantic for data validation, scikit-learn/NumPy for cosine similarity calculations.

- **Frontend:**
  - **React:** Created using Create React App.
  - **API Integration:** Axios or Fetch API for communication with the backend.
  - **UI Styling:** Using Material-UI or Bootstrap.

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your_username/amr-summarizer-prototype.git
   cd amr-summarizer-prototype

