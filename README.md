# AMR Summarizer Prototype

> **Thesis context** — This is the software prototype behind my BSc thesis
> **"Factual Consistency Evaluation Using AMR-Based Error Detection"** (Eötvös Loránd University, Faculty of Informatics, 2025;
> supervisors: Dr. Khawla Bouafia, Judit Ács / HUN-REN SZTAKI).
>
> **What it does:** detects factual errors in AI-generated (abstractive) summaries by parsing both the source article and the
> summary into **Abstract Meaning Representation (AMR)** graphs and aligning them (SMATCH-style graph comparison +
> Sentence-BERT sentence selection), returning a binary consistency verdict with visualized AMR graphs.
>
> Same research context as my co-authored paper *"Enhancing AMR Parsing with Group Relative Policy Optimization"*
> (XLLM Workshop @ ACL 2025 — my contribution there: dataset construction & evaluation).
>
> Status: research prototype (2025). Kept public as the reference implementation for the thesis.


This repository contains a prototype for generating, comparing, and visualizing Abstract Meaning Representation (AMR) graphs from summary and article texts. The project integrates NLP processing with a FastAPI backend and a React frontend, aiming for a robust, user-friendly experience with comprehensive error handling and GPU-accelerated processing.

---

## Overview

The project enables users to input a summary and an article, processes these texts to generate AMR graphs, visualizes them, and provides advanced tools for AMR graph alignment and comparison. Development has progressed through:

- **Phase 0**: Environment & AMR utilities
- **Phase 1**: SMATCH++-based alignment engine (`smatch_ext.py`)
- **Phase 2**: Overlap visualization (`visualizer.py` + `viewer.html`)

Phase 3 (UI integration) was not implemented; see *Current status* below.

---

## Key technical features

- **AMR parsing** of both article and summary into Penman graphs (`amrlib`), rendered to SVG via Graphviz.
- **Sentence selection** with Sentence-BERT embeddings and cosine similarity, so each summary sentence is compared against its most relevant source sentences rather than the whole article.
- **Graph alignment** using a SMATCH++-style node/edge matcher (`smatch_ext.py`) that reports the common subgraph between two AMRs.
- **Overlap visualization** (`visualizer.py`) that renders the two graphs side by side with shared nodes and edges highlighted.
- **HTTP API** exposing the pipeline through FastAPI with Pydantic request/response models.

## Stack

Python · FastAPI · Pydantic · amrlib · Penman · SMATCH++ · NetworkX · Sentence-BERT · spaCy · Graphviz · pytest · React

---

## Project Structure

```

AMR-SUMMARIZER-PROTOTYPE/
├── frontend/ # React app
│ ├── public/
│ └── src/
├── src/
│ └── amrsummarizer/ # Backend & core logic
│ ├── main.py # FastAPI app + endpoints
│ ├── models.py # Pydantic models
│ ├── pipeline.py # Sentence segmentation
│ ├── embeddings.py # Sentence-BERT embeddings
│ ├── similarity.py # Cosine similarity
│ ├── amr_parser.py # amrlib + Graphviz → SVG
│ ├── amr2nx.py # Penman → NetworkX (Phase 0)
│ ├── annotate.py # Overlap annotation logic
│ ├── metrics.py # Smatch-style F1 & consistency
│ ├── smatch_ext.py # SMATCH++ alignment (Phase 1)
│ ├── visualizer.py # SVG overlap generator (Phase 2)
│ ├── viewer.html # Static HTML to compare SVGs
│ └── sample_amrs/ # Sample .amr files for testing
├── tests/ # pytest suite
├── .gitignore
├── pytest.ini # PYTHONPATH=./src for tests
├── README.md
└── requirements.txt

```

---

## Quickstart: Phase 1 → Phase 2 Workflow

Follow these exact steps (from project root) on any machine with Python 3.8+.

### 1. Clone & Prepare

```bash
git clone https://github.com/masatonaut/amr-summarizer-prototype.git
cd amr-summarizer-prototype

# Create & activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install Python deps
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Phase 1 – Generate Alignment JSON

Two sample AMRs live in `src/amrsummarizer/sample_amrs/`.
You can drop any new `.amr` file there for testing.

```bash
python src/amrsummarizer/smatch_ext.py \
  --amr1 src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2 src/amrsummarizer/sample_amrs/sample2.amr \
  --output src/amrsummarizer/alignment.json
```

That writes:

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

### 3. Phase 2 – Produce Highlighted SVGs

```bash
python src/amrsummarizer/visualizer.py \
  --amr1      src/amrsummarizer/sample_amrs/sample1.amr \
  --amr2      src/amrsummarizer/sample_amrs/sample2.amr \
  --alignment src/amrsummarizer/alignment.json \
  --out1      src/amrsummarizer/sample1.svg \
  --out2      src/amrsummarizer/sample2.svg
```

You’ll get two SVGs with common nodes/edges highlighted in red, unique parts in gray.

### 4. Preview in Browser

Serve the HTML + SVGs so relative references load correctly:

```bash
cd src/amrsummarizer
python -m http.server 8001
```

Open → `http://localhost:8001/viewer.html`

---

## Core CLI Tools

### `smatch_ext.py` (Phase 1)

- **Path**: `src/amrsummarizer/smatch_ext.py`
- **Usage**: `--amr1 <file> --amr2 <file> --output <alignment.json>`
- **Function**: `compare_amr(amr1_str, amr2_str) -> { common_nodes, common_edges }`

### `visualizer.py` (Phase 2)

- **Path**: `src/amrsummarizer/visualizer.py`
- **Usage**: `--amr1 <file> --amr2 <file> --alignment <alignment.json> --out1 <svg1> --out2 <svg2>`
- **Function**: Renders two overlapped AMR graphs to SVG.

---

## Running the Backend & Frontend

#### Backend

```bash
# From project root
uvicorn src.amrsummarizer.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend
npm install
# Set API URL
echo "REACT_APP_API_URL=http://localhost:8000" > .env
npm start
```

---

## Testing

```bash
# From project root
PYTHONPATH=./src pytest -vv
```

---

## Current status

Research prototype, completed in 2025 alongside the thesis and no longer under active
development. Phases 0-2 (AMR utilities, SMATCH++ alignment, overlap visualization) are
implemented and covered by the test suite. Phase 3 was scoped but never built:

- An interactive web UI for exploring overlaps and differences node by node.
- Integration with annotation tooling for navigating non-overlapping sections.

The repository is kept public as the reference implementation for the thesis.
