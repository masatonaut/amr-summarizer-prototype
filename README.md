# amr-summarizer-prototype

This repository contains a prototype project for generating and comparing Abstract Meaning Representation (AMR) graphs from summary and article texts. The project integrates advanced NLP processing with a FastAPI backend and a React frontend. Our goal is to achieve a robust, user-friendly experience with comprehensive error handling and responsive design.

---

## Overview

The project utilizes a FastAPI backend for processing text and generating AMR graphs, and a React frontend (built with Create React App) for the user interface. Key features include:

- **Sentence segmentation** using spaCy.
- **Sentence embedding calculation** using Sentence-BERT (or a similar model) and cosine similarity to select the top three sentences.
- **AMR parsing** using amrlib to generate AMR graphs for both the summary and selected article sentences.
- **Enhanced error handling** on both the backend (via HTTPException) and the frontend (with clear user messages).
- **Unified, responsive UI design** using Material-UI and a custom PageLayout component.
- **Comprehensive testing** for backend endpoints using pytest.

---

## Components

### Backend

- **FastAPI & Uvicorn:** For building and serving API endpoints.
- **NLP Libraries:**
  - _spaCy_ for sentence segmentation.
  - _Sentence-BERT_ (or a similar model) for computing sentence embeddings.
  - _amrlib_ for AMR parsing.
- **Additional Tools:** Pydantic for data validation, scikit-learn/NumPy for cosine similarity calculations.
- **Error Handling:** Detailed input validation (e.g., checking for empty fields, overly long text, and simulated errors).

### Frontend

- **React:** Created using Create React App.
- **Routing:** Managed via React Router for navigation between input and results pages.
- **UI Components & Styling:** Using Material-UI for a modern, responsive design with a unified layout (PageLayout component) and consistent theming via ThemeProvider.
- **API Integration:** Utilizes the Fetch API to communicate with the backend.
- **Loading Indicators & Error Messages:** Provides visual feedback during processing and clear error messaging.

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
   Make sure that required libraries (spaCy, Sentence-BERT, amrlib, etc.) are installed. Also, download the spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. **Run the FastAPI Server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

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
   In the frontend directory, create a `.env` file (if not already present) with:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   PORT=3001
   ```
4. **Start the Development Server:**

   ```bash
   npm start
   ```

   This uses CRACO and Material-UI; the app should be accessible at http://localhost:3001.

5. **Production Build & Serve (Optional):**
   To build and serve the production version:
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
- **Error Handling:** Returns appropriate HTTP status codes (e.g., 400 for missing input, 500 for backend errors) with a JSON body containing an error message in the `detail` field.

### `/process_amr`

- **Method:** POST
- **Input:** Same as `/process_article`.
- **Output:** JSON containing:
  - `"summary_amr"`: The AMR graph for the summary.
  - `"top_sentence_amrs"`: Object mapping each top sentence to its corresponding AMR graph.
- **Error Handling:** Similar validations and error responses as above.

---

## Error Handling & Validation

### Frontend

- Validates that both Summary and Article fields are non-empty, not just whitespace.
- Checks for overly long inputs and displays clear error messages.
- Displays a loading spinner while waiting for the backend response.
- Catches network and server errors, showing user-friendly messages.

### Backend

- Uses FastAPI's HTTPException for input validation and error responses.
- Validates inputs (empty strings, excessive length) and returns clear error messages.
- Includes a simulation mechanism ("simulate error") for testing backend error handling.
- Comprehensive error responses are returned in JSON format.

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
  Use the browser to go through the complete user flow and validate error handling, loading indicators, and responsiveness.
- **(Optional) Automated Testing:**  
  (If needed in the future, consider using Cypress or Playwright, but currently testing is manual.)

---

## Deployment

- **Production Build:**  
  Create a production bundle with:
  ```bash
  npm run build
  ```
- **Static Server:**  
  Serve the production build using a static file server (e.g., with `serve` or another hosting solution).
- **Backend Deployment:**  
  Deploy the FastAPI backend using a platform of your choice (e.g., Docker, Heroku, etc.).

---

## Additional Notes

- **UI/UX Enhancements:**  
  The frontend uses Material-UI and a custom PageLayout component to provide a consistent, responsive design.
- **Version Control:**  
  All changes are managed via Git; refer to commit history for detailed progress.
- **Troubleshooting:**  
  Check browser Developer Tools for client-side errors and backend logs for server-side errors.
- **Future Enhancements:**  
  Consider adding automated end-to-end tests and further refining AMR graph visualization.

---

## Final Remarks

This project is approximately 90-95% complete. The core functionalities are implemented and integrated, with robust error handling and a unified UI design. The next steps involve final debugging, documentation updates, and preparing for a demo or deployment.
