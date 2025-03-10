# amr-summarizer-prototype

This repository contains a prototype for generating and comparing Abstract Meaning Representation (AMR) graphs from summary and article texts. The project integrates advanced NLP processing with a FastAPI backend and a React frontend. Our goal is to achieve a robust, user-friendly experience with comprehensive error handling, GPU-accelerated processing, and responsive design.

---

## Overview

The project consists of two main components:

- **Backend:** A FastAPI application that processes text, generates AMR graphs using amrlib, and converts these graphs into SVG visualizations.
- **Frontend:** A React application (built with Create React App) that provides a user-friendly interface for entering text and displaying results.

Key features include:

- **Sentence Segmentation:** Performed using spaCy.
- **Sentence Embedding Calculation:** Uses Sentence-BERT (or a similar model) to compute embeddings and select the top three sentences via cosine similarity.
- **AMR Parsing & Visualization:** Uses amrlib and penman to generate AMR graphs and Graphviz to produce SVG images.
- **GPU Acceleration & Memory Management:** The backend leverages GPU(s) for faster model inference. After processing, the model is moved to the CPU and the CUDA cache is cleared to free up memory.
- **Error Handling:** Both backend and frontend implement robust error handling to provide clear, user-friendly messages.
- **Responsive UI:** The frontend uses Material-UI and a custom PageLayout component for a consistent, responsive design.

---

## Components

### Backend

- **Frameworks & Tools:** FastAPI, Uvicorn, Gunicorn
- **NLP Libraries:**
  - _spaCy_ for sentence segmentation.
  - _Sentence-BERT_ for embedding calculation.
  - _amrlib_ for AMR parsing.
  - _penman_ and _graphviz_ for converting AMR graphs to SVG.
- **GPU & Memory Management:**  
  The backend is designed to run on GPU and includes steps to move the model to CPU and clear CUDA cache after processing.
- **Data Validation:**  
  Pydantic is used for input validation. The backend also simulates errors for testing purposes.

### Frontend

- **Frameworks & Tools:** React (created with Create React App), React Router, Material-UI, and CRACO.
- **Routing & API Integration:**  
  The frontend communicates with the backend API via the Fetch API. Environment variables (in a `.env` file) configure the API URL.
- **Visualization:**  
  The results page displays the SVG images generated on the backend by injecting the SVG strings directly into the DOM.

---

## Setup Instructions

### Backend Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/masatonaut/amr-summarizer-prototype.git
   cd amr-summarizer-prototype
   ```
2. **Set Up the Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Make sure to download the required spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. **Run the FastAPI Server with GPU Specification (if applicable):**
   ```bash
   CUDA_VISIBLE_DEVICES=0 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   This command specifies the GPU to use (e.g., GPU 0) and starts the server on port 8000.

### Frontend Setup

1. **Navigate to the Frontend Directory:**
   ```bash
   cd frontend
   ```
2. **Install Dependencies:**
   ```bash
   npm install
   ```
3. **Create a `.env` File:**  
   In the frontend directory, create a `.env` file with the following contents:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   PORT=3001
   ```
4. **Start the Development Server:**

   ```bash
   npm start
   ```

   The app should now be accessible at [http://localhost:3001](http://localhost:3001).

5. **Production Build & Serve (Optional):**
   To build and serve the production version locally:
   ```bash
   npm run build
   npm install serve --save-dev
   npm run serve
   ```

---

## API Endpoints

### `/process_article`

- **Method:** POST
- **Input:** JSON with keys:
  - `summary`: Summary text.
  - `article`: Article text.
- **Output:** JSON containing:
  - `"top_sentences"`: Array of the top 3 selected sentences.
  - `"similarity_scores"`: Array of corresponding cosine similarity scores.
- **Error Handling:** Returns appropriate HTTP status codes (e.g., 400 for missing input, 500 for simulated errors) with a JSON body containing an error message in the `detail` field.

### `/process_amr`

- **Method:** POST
- **Input:** Same as `/process_article`.
- **Output:** JSON containing:
  - `"summary_amr"`: The SVG visualization of the AMR graph for the summary.
  - `"top_sentence_amrs"`: Object mapping each top sentence to its corresponding SVG visualization.
- **Error Handling:** Similar validations and error responses as the `/process_article` endpoint.

---

## Memory Management & GPU Usage

To prevent CUDA out-of-memory errors during processing, the backend code moves the model to the CPU and clears the GPU cache after processing:

```python
stog = amrlib.load_stog_model()
graphs = stog.parse_sents([text])
stog.model.to('cpu')
del stog
gc.collect()
torch.cuda.empty_cache()
```

This is especially important when running on GPUs to ensure stable performance.

---

## Testing

### Backend

- **Unit/Integration Tests:**  
  Run pytest to execute tests for API endpoints:
  ```bash
  pytest backend/test_main.py
  ```

### Frontend

- **Manual Testing:**  
  Use your browser to verify the complete user flow, including error handling and the visualization of AMR graphs.
- **(Optional) Automated Testing:**  
  Consider using tools like Cypress or Playwright in the future for end-to-end testing.

---

## Final Remarks

This project currently runs and is tested on localhost. All core functionalities have been implemented, including robust error handling and GPU-accelerated processing with proper memory management. The next steps involve final debugging and further enhancing the AMR graph visualization based on feedback.

Please refer to this README for setup and deployment instructions when running the project locally.
