import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pytest

from pipeline import segment_sentences
from similarity import top_k_sentences
from amr_parser import parse_amr

def test_segment_sentences_basic():
    assert segment_sentences("Hello world. This is a test.") == ["Hello world.", "This is a test."]

def test_top_k_sentences_simple_sorting():
    summary_emb = np.array([1.0, 0.0])
    sent_embs = [
        np.array([1.0, 0.0]),
        np.array([0.0, 1.0]),
        np.array([0.5, 0.5]),
    ]
    sents = ["A","B","C"]
    top_sents, scores = top_k_sentences(summary_emb, sent_embs, sents, k=2)
    assert top_sents == ["A","C"]
    assert pytest.approx(scores[0], rel=1e-3) == 1.0

def test_parse_amr_contains_buy():
    amr = parse_amr("John bought a car from Mary.")
    assert "buy-01" in amr
