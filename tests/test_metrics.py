from amrsummarizer.metrics import smatch_f1, is_factually_consistent

# A minimal AMR string for testing
SAME_AMR = """
(x / test
   :arg0 (y / yes)
   :arg1 (z / zero))
"""


def test_smatch_perfect():
    """SMATCH F1 should be 1.0 when comparing identical AMRs."""
    score = smatch_f1(SAME_AMR, SAME_AMR)
    assert score == 1.0


def test_binary_consistency_true():
    """Binary check returns (True, 1.0) when summary == source AMR."""
    ok, score = is_factually_consistent(SAME_AMR, [SAME_AMR], threshold=0.9)
    assert ok is True
    assert score == 1.0


def test_binary_consistency_false():
    """Binary check returns (False, < threshold) for mismatched AMRs."""
    DIFFERENT_AMR = "(a / alpha)"
    ok, score = is_factually_consistent(SAME_AMR, [DIFFERENT_AMR], threshold=0.5)
    assert ok is False
    assert 0.0 <= score < 0.5
