from penman import decode

def extract_triples(amr_str: str) -> set[tuple]:
    """
    Parse an AMR in Penman format into a penman.Graph and
    return the set of (source, role, target) triples.
    """
    graph = decode(amr_str)
    return set(graph.triples)

def smatch_f1(amr1: str, amr2: str) -> float:
    """
    Compute a simple Smatch‐style F1 between two AMR strings.
    Precision = |T2 ∩ T1| / |T2|
    Recall    = |T1 ∩ T2| / |T1|
    F1        = 2PR/(P+R)
    """
    t1 = extract_triples(amr1)
    t2 = extract_triples(amr2)

    # Edge cases
    if not t1 and not t2:
        return 1.0
    if not t1 or not t2:
        return 0.0

    inter = t1 & t2
    p = len(inter) / len(t2)
    r = len(inter) / len(t1)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)

def is_factually_consistent(
    summary_amr: str,
    source_amrs: list[str],
    threshold: float = 0.8
) -> tuple[bool, float]:
    """
    Binary consistency check: what fraction of summary triples
    appear in the union of all source_amrs?  Return (ok, score).
    """
    summary_triples = extract_triples(summary_amr)

    merged = set()
    for amr in source_amrs:
        merged |= extract_triples(amr)

    if not summary_triples:
        score = 1.0
    else:
        common = summary_triples & merged
        score = len(common) / len(summary_triples)

    return (score >= threshold, score)
