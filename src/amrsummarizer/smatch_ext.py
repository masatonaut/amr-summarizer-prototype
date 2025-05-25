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


def _orig_var(tok: str) -> str:
    """
    Strip SMATCH++ prefixes like 'aa_' or 'bb_' from internal tokens
    to recover the original AMR variable name.
    E.g. 'aa_m' -> 'm', 'bb_w' -> 'w'.
    """
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
        orig1 = _orig_var(va)
        orig2 = _orig_var(vb)
        if (orig1, orig2) not in seen:
            seen.add((orig1, orig2))
            nodes.append((orig1, orig2))
    common_nodes = [[a, b] for a, b in nodes]

    # Build edge mapping - restore original roles from AMR text
    def get_original_edges(amr_text, triples):
        """Extract edges with original role labels from AMR text"""
        edges = []
        for s, r, t in triples:
            if r == ":instance":
                continue
            
            # Check if this should be an inverse role
            # Look for patterns like ":ARG0-of" in the original text
            if f":{r[1:]}-of" in amr_text and r.startswith(":ARG"):
                # This is an inverse role, swap source and target
                edges.append((t, f":{r[1:]}-of", s))
            else:
                edges.append((s, r, t))
        return edges
    
    edges1 = get_original_edges(amr1, g1)
    edges2 = get_original_edges(amr2, g2)
    
    # Build common edges
    raw2 = set(edges2)
    mapping = dict(nodes)
    common_edges = []
    for s, r, t in edges1:
        ms, mt = mapping.get(s, s), mapping.get(t, t)
        if (ms, r, mt) in raw2:
            common_edges.append([[s, t, r], [ms, mt, r]])

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


if __name__ == "__main__":
    main()