# AMR Summarizer Prototype

This repository contains a prototype for generating, comparing, and visualizing Abstract Meaning Representation (AMR) graphs from summary and article texts. The project integrates NLP processing with a FastAPI backend and a React frontend, aiming for a robust, user-friendly experience with comprehensive error handling and GPU-accelerated processing.

---

## Overview

The project enables users to input a summary and an article, processes these texts to generate AMR graphs, visualizes them, and provides advanced tools for AMR graph alignment and comparison. It consists of two main components:

- **Backend**: A FastAPI application (`src/amrsummarizer/main.py`) that handles text processing, AMR graph generation, SVG visualization, AMR comparison, and serves the core logic.
- **Frontend**: A React application (in the `frontend` directory) that provides a user interface for text input and displaying results.

Development has progressed through several phases, building a foundation for AMR processing (Phase 0), developing an AMR alignment engine using SMATCH++ (Phase 1), and creating scripts for visualizing graph overlaps (Phase 2). Phase 3, focusing on UI integration, is planned.

---

## Project Structure

The project is organized as follows:

```

AMR-SUMMARIZER-PROTOTYPE/
├── .vscode/ # VSCode settings
├── frontend/ # React frontend application
│ ├── public/
│ ├── src/
│ ├── package.json
│ └── ...
├── src/
│ └── amrsummarizer/ # FastAPI backend application and core logic
│ ├── **init**.py
│ ├── main.py # FastAPI app definition and endpoints
│ ├── models.py # Pydantic models
│ ├── pipeline.py # Sentence segmentation
│ ├── embeddings.py # Embedding generation
│ ├── similarity.py # Similarity calculation
│ ├── amr*parser.py # AMR parsing and SVG conversion logic
│ ├── amr2nx.py # Penman to NetworkX conversion (Phase 0)
│ ├── annotate.py # Annotation logic
│ ├── metrics.py # Factual consistency, Smatch
│ ├── smatch_ext.py # SMATCH++ extensions for comparison (Phase 1)
│ ├── visualizer.py # Visualization script (Phase 2)
│ ├── viewer.html # HTML viewer for static comparison
│ └── sample_amrs/ # Sample AMR files for testing
├── tests/ # Pytest tests for the backend
│ ├── test*\*.py
├── venv/ # Python virtual environment (if created here)
├── .gitignore
├── pytest.ini # Pytest configuration (e.g., pythonpath)
├── README.md
└── requirements.txt # Backend Python dependencies

```

---

## Key Features

- **Sentence Segmentation**: Performed using spaCy.
- **Sentence Embedding Calculation**: Uses Sentence-BERT (or a similar model) to compute embeddings and select top sentences via cosine similarity.
- **AMR Parsing & Visualization**: Generates AMR graphs and produces SVG images for display.
- **AMR Alignment & Comparison**: Implements automated AMR alignment using SMATCH++ (via `smatch_ext.py`) to identify common nodes and edges.
- **Overlap Visualization**: Custom scripts (`visualizer.py`) display two AMR graphs side-by-side, highlighting commonalities based on SMATCH++ alignment.
- **GPU Acceleration & Memory Management**: The backend can leverage GPU(s) for faster model inference with memory management.
- **Error Handling**: Robust error handling in both backend and frontend.
- **Responsive UI**: Frontend uses Material-UI for a consistent, responsive design.

---

## Core Components

### Backend

- **Frameworks & Tools**: FastAPI, Uvicorn
- **NLP Libraries & Modules**:
  - `src/amrsummarizer/pipeline.py`: spaCy for sentence segmentation.
  - `src/amrsummarizer/embeddings.py`: Sentence-BERT for embeddings.
  - `src/amrsummarizer/similarity.py`: Cosine similarity for sentence selection.
  - `src/amrsummarizer/amr_parser.py`: AMR parsing and Graphviz for SVG conversion.
  - `src/amrsummarizer/metrics.py`: Factual consistency checks.
  - `src/amrsummarizer/smatch_ext.py`: Core SMATCH++ based comparison logic. (Phase 1)
  - `src/amrsummarizer/amr2nx.py`: Converts Penman graphs to NetworkX. (Phase 0)
  - `src/amrsummarizer/visualize_overlap.py`: Script for generating overlap visualizations. (Phase 2)
- **GPU & Memory Management**: Designed for GPU execution with CUDA cache clearing.
- **Data Validation**: Pydantic models (`src/amrsummarizer/models.py`) for input validation.

### Frontend

- **Frameworks & Tools**: React (Create React App), React Router, Material-UI, CRACO.
- **API Integration**: Communicates with the backend API. Environment variables (`frontend/.env`) configure the API URL.
- **Visualization**: Displays SVG images from the backend.

---

## Quickstart Guide: Phase 1 → Phase 2 AMR Alignment & Visualization

Use this guide to take two AMR files, generate their SMATCH++ alignment, produce highlighted SVGs, and preview them in a static HTML viewer. Team members can follow these exact steps on any machine with Python 3.8+ and a virtualenv.

### Prerequisites

1.  **Clone & enter the repo**

    ```bash
    git clone [https://github.com/masatonaut/amr-summarizer-prototype.git](https://github.com/masatonaut/amr-summarizer-prototype.git)
    cd amr-summarizer-prototype
    ```

    _([USER VERIFICATION: Confirm if the repository URL is correct.]_)

2.  **Activate your virtual environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download spaCy model**
    ```bash
    python -m spacy download en_core_web_sm
    ```

### AMR Sample Files

By default, we include two sample AMR files under:
`src/amrsummarizer/sample_amrs/`

- `sample1.amr`
- `sample2.amr`

If you have additional AMR files to test, please place them in the same `src/amrsummarizer/sample_amrs/` directory.

### Phase 1: Generate Alignment JSON

Run the SMATCH++ alignment tool (`smatch_ext.py`) on your two AMRs. This script is assumed to be runnable and accept command-line arguments as shown.
_(Run commands from the project root directory, e.g., `amr-summarizer-prototype/`)_

```bash
python src/amrsummarizer/smatch_ext.py \
  --amr1 src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2 src/amrsummarizer/sample_amrs/sample2.amr \
  --output src/amrsummarizer/alignment.json
```

**Output**: This will generate an `alignment.json` file in `src/amrsummarizer/` with a structure similar to:

```json
{
  "common_nodes": [
    ["m", "m"],
    ["l", "l"],
    ["w", "w"]
  ],
  "common_edges": [
    [
      ["m", "l", ":ARG0-of"],
      ["m", "l", ":ARG0-of"]
    ],
    [
      ["l", "w", ":ARG1"],
      ["l", "w", ":ARG1"]
    ]
  ]
}
```

### Phase 2: Visualize Overlap

Generate two SVGs highlighting the overlap using the `visualizer.py` script and the `alignment.json` from the previous step.
_(Run commands from the project root directory)_

```bash
python src/amrsummarizer/visualizer.py \
  --amr1      src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2      src/amrsummarizer/sample_amrs/sample2.amr \
  --alignment src/amrsummarizer/alignment.json \
  --out1      src/amrsummarizer/sample1.svg \
  --out2      src/amrsummarizer/sample2.svg
```

**Outputs**:

- `src/amrsummarizer/sample1.svg`
- `src/amrsummarizer/sample2.svg`

In these SVGs, common nodes might appear in red/pink, and common edges in bold red (actual highlighting may vary based on `visualizer.py` implementation).

### Preview with Static HTML Viewer

To properly view the generated SVGs (especially if they have relative links or complex structures), serve the `viewer.html` and the SVGs over HTTP.

1.  **Navigate to the directory containing `viewer.html` and the SVGs:**
    ```bash
    cd src/amrsummarizer
    ```
2.  **Start a simple Python HTTP server:**
    ```bash
    python -m http.server 8001
    ```
3.  **Open in your browser:**
    Navigate to `http://localhost:8001/viewer.html`

This should display `sample1.svg` and `sample2.svg` side-by-side with their overlaps highlighted.

### Full Command Summary (End-to-End Workflow)

```bash
# (From project root)
# Activate env & install (if not already done)
# source venv/bin/activate
# pip install -r requirements.txt
# python -m spacy download en_core_web_sm

# Phase 1: Generate alignment.json
python src/amrsummarizer/smatch_ext.py \
  --amr1 src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2 src/amrsummarizer/sample_amrs/sample2.amr \
  --output src/amrsummarizer/alignment.json

# Phase 2: Generate highlighted SVGs
python src/amrsummarizer/visualizer.py \
  --amr1      src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2      src/amrsummarizer/sample_amrs/sample2.amr \
  --alignment src/amrsummarizer/alignment.json \
  --out1      src/amrsummarizer/sample1.svg \
  --out2      src/amrsummarizer/sample2.svg

# Preview SVGs
cd src/amrsummarizer
python -m http.server 8001
# Then open http://localhost:8001/viewer.html in your browser.
# Remember to 'cd ..' back to the project root for other commands.
```

Now anyone on the team can reproduce the full Phase 1 → Phase 2 workflow end-to-end.

---

## Key Developed Tools & Usage (Further Details)

This section provides more details on the individual tools. For a practical end-to-end example of `smatch_ext.py` (CLI) and `visualizer.py`, see the **Quickstart Guide** above.

### 1. AMR Alignment Engine (`smatch_ext.py`) - Phase 1

This module provides the core logic for aligning two AMR graphs using an extended SMATCH++ approach to identify common nodes and edges.

- **Location**: `src/amrsummarizer/smatch_ext.py`
- **Primary Function (Programmatic Use)**: `compare_amr(amr1_str: str, amr2_str: str) -> AlignmentData`

  - (Note: `AlignmentData` is a placeholder for the actual return type, which should detail matched nodes/edges as seen in the `alignment.json` example in the Quickstart.)
  - **Example**:

    ```python
    from amrsummarizer.smatch_ext import compare_amr

    amr_string_1 = "(a / apple)" # Example AMR string
    amr_string_2 = "(b / big-apple)" # Example AMR string

    alignment_results = compare_amr(amr_string_1, amr_string_2)
    # Process alignment_results
    print(alignment_results)
    ```

- **Command-Line Interface**: See the **Quickstart Guide** for a detailed command-line example of using `smatch_ext.py` to generate an `alignment.json` file.
- **FastAPI Endpoint (`/compare_amr`)**: Provides API access to the alignment engine.
  - (Details in the "API Endpoints" section below. `[USER VERIFICATION: Please confirm if this endpoint is implemented in main.py and update its specifications accordingly.]`)

### 2. Overlap Visualization Script (`visualizer.py`) - Phase 2

This script generates a visual comparison of two AMR graphs, highlighting their overlapping sections based on a pre-computed alignment JSON file.

- **Location**: `src/amrsummarizer/visualizer.py`
- **Functionality**: Takes two AMR files and an `alignment.json` (from `smatch_ext.py`) as input, and generates two SVG files with common nodes/edges highlighted.
- **Command-Line Usage**: See the **Quickstart Guide** for a detailed command-line example. The output SVGs can be viewed using `viewer.html` as described in the Quickstart.

### 3. AMR to NetworkX Conversion (`amr2nx.py`) - Phase 0

A foundational module for converting Penman AMR graph objects into NetworkX graph objects, enabling the use of NetworkX's rich set of graph analysis algorithms.

- **Location**: `src/amrsummarizer/amr2nx.py`
- **Programmatic Usage**: Import the conversion function (e.g., `penman_to_networkx`) in your Python scripts.

  ```python
  from penman import decode
  from amrsummarizer.amr2nx import penman_to_networkx # [USER VERIFICATION: Please confirm the function name.]

  amr_string = "(g / go :ARG0 (i / i))"
  penman_graph = decode(amr_string) # Assuming you have a penman.Graph object
  networkx_graph = penman_to_networkx(penman_graph)
  # Now you can use networkx_graph with NetworkX functions
  print(f"Number of nodes in NetworkX graph: {networkx_graph.number_of_nodes()}")
  ```

---

## Setup Instructions

### Backend Setup

1.  **Clone the Repository:** (If not done in Quickstart)
    ```bash
    git clone [https://github.com/masatonaut/amr-summarizer-prototype.git](https://github.com/masatonaut/amr-summarizer-prototype.git)
    cd amr-summarizer-prototype
    ```
    _([USER VERIFICATION: Confirm if the repository URL is correct.]_)
2.  **Set Up the Virtual Environment:** (If not done in Quickstart)
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:** (If not done in Quickstart)
    ```bash
    pip install -r requirements.txt
    ```
    Make sure to download the required spaCy model (if not done in Quickstart):
    ```bash
    python -m spacy download en_core_web_sm
    ```
4.  **Run the FastAPI Server:**
    (From the project root directory)
    ```bash
    uvicorn src.amrsummarizer.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    To specify a GPU (e.g., GPU 0), you can prefix the command:
    ```bash
    CUDA_VISIBLE_DEVICES=0 uvicorn src.amrsummarizer.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### Frontend Setup

1.  **Navigate to the Frontend Directory:**
    (From the project root directory)
    ```bash
    cd frontend
    ```
2.  **Install Dependencies:**
    ```bash
    npm install
    ```
3.  **Create a `.env` File:**
    In the `frontend` directory, create a `.env` file with the following contents:
    ```env
    REACT_APP_API_URL=http://localhost:8000
    PORT=3001
    ```
4.  **Start the Development Server:**

    ```bash
    npm start
    ```

    The app should now be accessible at `http://localhost:3001`.

5.  **Production Build & Serve (Optional):**
    ```bash
    npm run build
    npm install serve --save-dev # If not already installed
    npm run serve # Or serve -s build
    ```

---

## API Endpoints

(Served by the backend at `http://localhost:8000`)

### `/ping`

- **Method**: GET
- **Output**: `{"message": "Pong!"}`

### `/` (Root)

- **Method**: GET
- **Output**: `{"message": "Hello from the AMR Summarizer API!"}`

### `/process_article`

- **Method**: POST
- **Input (JSON)**: `{"summary": "Summary text.", "article": "Article text."}`
- **Output (JSON)**: `{"top_sentences": ["Sentence 1...", ...], "similarity_scores": [0.98, ...]}`
- **Error Handling**: Returns appropriate HTTP status codes (e.g., 400, 500) with `{"detail": "Error message"}`.

### `/process_amr`

- **Method**: POST
- **Input (JSON)**: Same as `/process_article`.
- **Output (JSON)**:
  ```json
  {
    "summary_svg": "<svg>...</svg>",
    "top_sentence_svgs": {
      "Sentence 1...": "<svg>...</svg>",
      ...
    },
    "consistency_score": 0.85,
    "is_consistent": true
  }
  ```
- **Error Handling**: Similar to `/process_article`.

### `/compare_amr` (Developed in Phase 1)

- `[USER VERIFICATION: If this endpoint is implemented in main.py, please update the specifications below to match its actual behavior. If not yet implemented, state so or remove this section.]`
- **Method**: POST (assumption)
- **Input (JSON)**: (Example - please confirm)
  ```json
  {
    "amr_string1": "(a / amr-graph ...)",
    "amr_string2": "(b / another-amr-graph ...)"
  }
  ```
- **Output (JSON)**: (Example - based on `smatch_ext.py`'s expected output, please confirm)
  ```json
  {
    "common_nodes": [["node_id_amr1_1", "node_id_amr2_1"], ...],
    "common_edges": [[["u1","r1","v1"], ["u2","r2","v2"]], ...],
    "smatch_score": 0.90 // Or other relevant SMATCH++ output details
  }
  ```
- **Description**: Takes two AMR strings and returns detailed alignment information including common nodes, common edges, and potentially a SMATCH score.

---

## Memory Management & GPU Usage

To prevent CUDA out-of-memory errors when using GPU-accelerated models, the backend may include code to move models to CPU and clear the GPU cache after processing:

```python
# Example:
# import torch, gc
# model.to('cpu')
# del model
# gc.collect()
# torch.cuda.empty_cache()
```

This practice is important for stable performance on GPU-enabled systems. Ensure such mechanisms are in place for any large models used.

---

## Testing

### Backend

- **Unit/Integration Tests**: Run pytest from the project root directory. `pytest.ini` is configured to help pytest find the `src` modules.
  ```bash
  # Run all tests
  PYTHONPATH=./src pytest
  # Run tests in a specific file (e.g., test_process_amr.py)
  PYTHONPATH=./src pytest tests/test_process_amr.py
  # Run with more verbosity
  PYTHONPATH=./src pytest -vv
  ```

### Frontend

- **Manual Testing**: Use your browser to verify the complete user flow.
- **Automated Testing**: Consider Jest for unit tests and Cypress or Playwright for end-to-end testing.

---

## Future Work (Phase 3 & Beyond)

Phase 3 plans include:

- **Annotation Tool Integration/Prototype UI**:
  - Investigating integration with existing tools (e.g., BRAT, WebAnno) or developing a standalone prototype UI (e.g., Flask/Django + React + D3).
  - Implementing a view for parallel AMR display with highlighted overlaps and features to focus on differences.
  - Optional: Interactive features like node-click details and difference reporting.

Further enhancements could involve performance optimizations, expanded AMR comparison metrics, and more sophisticated UI/UX for analysis.

---

## Final Remarks

This prototype provides a foundation for AMR-based text summarization analysis, comparison, and visualization. The phased development has added significant capabilities in AMR alignment and understanding.
