import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pytest

from pipeline import segment_sentences
from similarity import top_k_sentences
from amr_parser import parse_amr

def test_segment_sentences_basic():
    """
    Unit test: segment_sentences should split text into individual sentences.
    """
    text = "Hello world. This is a test."
    expected = ["Hello world.", "This is a test."]
    assert segment_sentences(text) == expected

def test_top_k_sentences_simple_sorting():
    """
    Unit test: top_k_sentences should select the top-k most similar sentences
    based on cosine similarity.
    """
    # Define a simple 2D embedding space
    summary_emb = np.array([1.0, 0.0])
    sent_embs = [
        np.array([1.0, 0.0]),  # identical → similarity 1.0
        np.array([0.0, 1.0]),  # orthogonal → similarity 0.0
        np.array([0.5, 0.5]),  # 45° angle → similarity ≈0.707
    ]
    sents = ["A", "B", "C"]
    top_sents, scores = top_k_sentences(summary_emb, sent_embs, sents, k=2)
    # Expect the identical and next-most similar
    assert top_sents == ["A", "C"]
    # Check the highest score is approximately 1.0
    assert pytest.approx(scores[0], rel=1e-3) == 1.0

def test_parse_amr_contains_buy():
    """
    Unit test: parse_amr should return a Penman-formatted string
    containing the AMR instance 'buy-01' for the input sentence.
    """
    amr = parse_amr("John bought a car from Mary.")
    assert "buy-01" in amr
