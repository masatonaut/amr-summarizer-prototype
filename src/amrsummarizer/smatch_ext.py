import json
import argparse
from penman import decode
from smatchpp import Smatchpp, solvers, interfaces


class RawReader(interfaces.GraphReader):
    """
    Return raw penman.decode(...) triples so we keep original variables & roles.
    """
    def _string2graph(self, penman_str: str):
        return decode(penman_str).triples


def _orig_var(tok) -> str:
    """
    Strip SMATCH++ prefixes like 'aa_' or 'bb_' from internal tokens
    to recover the original AMR variable name.
    E.g. 'aa_m' -> 'm', 'bb_w' -> 'w'.
    Returns empty string if tok is None.
    """
    if tok is None:
        return ""
    if not isinstance(tok, str):
        tok = str(tok)
    if "_" in tok:
        parts = tok.split("_", 1)
        return parts[1]
    return tok


def compare_amr(amr1: str, amr2: str) -> dict:
    # Initialize SMATCH++ with no standardization
    measure = Smatchpp(
        alignmentsolver    = solvers.ILP(),
        graph_reader       = RawReader(),
        graph_standardizer = None,
    )

    # Load the raw triples
    g1 = measure.graph_reader.string2graph(amr1)
    g2 = measure.graph_reader.string2graph(amr2)

    # Prepare & align
    g1p, g2p, v1, v2 = measure.graph_pair_preparer.prepare_get_vars(g1, g2)
    alignment, var_index, _ = measure.graph_aligner.align(g1p, g2p, v1, v2)

    # Build node mapping, stripping SMATCH++ prefixes back to original vars
    var_map = measure.graph_aligner._get_var_map(alignment, var_index)
    seen, nodes = set(), []
    for va, vb in var_map:
        # Skip None values
        if va is None or vb is None:
            continue
        orig1 = _orig_var(va)
        orig2 = _orig_var(vb)
        # Skip empty strings
        if not orig1 or not orig2:
            continue
        if (orig1, orig2) not in seen:
            seen.add((orig1, orig2))
            nodes.append((orig1, orig2))
    common_nodes = [[a, b] for a, b in nodes]

    # Build edge mapping - keep original representation from triples
    def normalize_edges(triples):
        """Convert triples to normalized edges, preserving original role form"""
        edges = []
        for s, r, t in triples:
            # Skip None values and instance relations
            if s is None or r is None or t is None or r == ":instance":
                continue
            edges.append((s, r, t))
        return edges
    
    edges1 = normalize_edges(g1)
    edges2 = normalize_edges(g2)
    
    # Build common edges by comparing normalized forms
    edges1_set = set(edges1)
    edges2_set = set(edges2)
    mapping = {k: v for k, v in nodes if k and v}  # Filter out empty strings
    
    common_edges = []
    
    # Check for direct matches first
    for s1, r1, t1 in edges1:
        # Map to corresponding nodes in g2
        s2_mapped = mapping.get(s1, s1)
        t2_mapped = mapping.get(t1, t1)
        
        if (s2_mapped, r1, t2_mapped) in edges2_set:
            common_edges.append([[s1, t1, r1], [s2_mapped, t2_mapped, r1]])
    
    return {"common_nodes": common_nodes, "common_edges": common_edges}


def main():
    p = argparse.ArgumentParser(description="Auto‐generate alignment.json")
    p.add_argument("--amr1",   required=True, help="First AMR file")
    p.add_argument("--amr2",   required=True, help="Second AMR file")
    p.add_argument("--output", default="alignment.json", help="Output JSON path")
    args = p.parse_args()

    s1 = open(args.amr1, encoding="utf-8").read().strip()
    s2 = open(args.amr2, encoding="utf-8").read().strip()

    alignment = compare_amr(s1, s2)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(alignment, f, indent=2)

    print(f"Wrote alignment to {args.output}")
    print(f"Found {len(alignment['common_nodes'])} common nodes and {len(alignment['common_edges'])} common edges")


if __name__ == "__main__":
    main()