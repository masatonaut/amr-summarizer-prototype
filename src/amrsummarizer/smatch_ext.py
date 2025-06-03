import json
import argparse
from penman import decode
from smatchpp import Smatchpp, solvers, interfaces


class RawReader(interfaces.GraphReader):
    """
    Return raw penman.decode(...) triples so we keep original variables & roles.
    Handles AMR files with comment lines and proper string formatting.
    """
    def _string2graph(self, penman_str: str):
        import re
        
        content = penman_str.strip()
        
        # Remove outer quotes if the entire content is wrapped in quotes
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        # Find the first occurrence of '(' which should be the start of the AMR
        paren_start = content.find('(')
        if paren_start == -1:
            raise ValueError("Could not find AMR structure (no opening parenthesis found)")
        
        # Extract everything from the first '(' to the end
        amr_content = content[paren_start:].strip()
        
        # Fix double quotes in string literals (""word"" -> "word")
        amr_content = re.sub(r'""([^"]*?)""', r'"\1"', amr_content)
        
        # Additional cleanup: remove any trailing quotes that might be left
        amr_content = amr_content.rstrip('"')
        
        try:
            result = decode(amr_content)
            return result.triples
        except Exception as e:
            print(f"Error parsing AMR: {e}")
            print(f"Original content length: {len(penman_str)}")
            print(f"AMR content length: {len(amr_content)}")
            print(f"First 300 chars of AMR: {repr(amr_content[:300])}")
            print(f"Last 100 chars of AMR: {repr(amr_content[-100:])}")
            raise


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


def extract_all_nodes(triples):
    """
    Extract all nodes (variables) from AMR triples, filtering out instance relations.
    Returns a set of all variable names.
    """
    nodes = set()
    for s, r, t in triples:
        if s is None or r is None or t is None:
            continue
        if r == ":instance":
            # For instance relations, only add the source variable
            if s:
                nodes.add(s)
        else:
            # For other relations, add both source and target if they are variables
            if s and isinstance(s, str):
                nodes.add(s)
            # Only add target if it looks like a variable (not a constant/literal)
            if t and isinstance(t, str) and not (t.startswith('"') or t.startswith("'")):
                nodes.add(t)
    return nodes


def extract_all_edges(triples):
    """
    Extract all edges from AMR triples, excluding instance relations.
    Returns a set of (source, role, target) tuples.
    """
    edges = set()
    for s, r, t in triples:
        if s is None or r is None or t is None or r == ":instance":
            continue
        edges.add((s, r, t))
    return edges


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

    # Extract all nodes from both graphs
    all_nodes_g1 = extract_all_nodes(g1)
    all_nodes_g2 = extract_all_nodes(g2)

    # Extract all edges from both graphs
    all_edges_g1 = extract_all_edges(g1)
    all_edges_g2 = extract_all_edges(g2)

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

    # Find uncommon nodes
    common_nodes_g1 = {pair[0] for pair in nodes}
    common_nodes_g2 = {pair[1] for pair in nodes}
    
    uncommon_nodes_g1 = list(all_nodes_g1 - common_nodes_g1)
    uncommon_nodes_g2 = list(all_nodes_g2 - common_nodes_g2)
    
    uncommon_nodes = {
        "amr1_only": sorted(uncommon_nodes_g1),
        "amr2_only": sorted(uncommon_nodes_g2)
    }

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
    common_edges_g1 = set()
    common_edges_g2 = set()
    
    # Check for direct matches first
    for s1, r1, t1 in edges1:
        # Map to corresponding nodes in g2
        s2_mapped = mapping.get(s1, s1)
        t2_mapped = mapping.get(t1, t1)
        
        if (s2_mapped, r1, t2_mapped) in edges2_set:
            common_edges.append([[s1, t1, r1], [s2_mapped, t2_mapped, r1]])
            common_edges_g1.add((s1, r1, t1))
            common_edges_g2.add((s2_mapped, r1, t2_mapped))

    # Find uncommon edges
    uncommon_edges_g1 = list(all_edges_g1 - common_edges_g1)
    uncommon_edges_g2 = list(all_edges_g2 - common_edges_g2)
    
    # Convert to list format for JSON serialization
    uncommon_edges = {
        "amr1_only": [[s, t, r] for s, r, t in sorted(uncommon_edges_g1)],
        "amr2_only": [[s, t, r] for s, r, t in sorted(uncommon_edges_g2)]
    }

    return {
        "common_nodes": common_nodes, 
        "common_edges": common_edges,
        "uncommon_nodes": uncommon_nodes,
        "uncommon_edges": uncommon_edges,
        "statistics": {
            "total_nodes_amr1": len(all_nodes_g1),
            "total_nodes_amr2": len(all_nodes_g2),
            "common_nodes_count": len(common_nodes),
            "uncommon_nodes_amr1_count": len(uncommon_nodes_g1),
            "uncommon_nodes_amr2_count": len(uncommon_nodes_g2),
            "total_edges_amr1": len(all_edges_g1),
            "total_edges_amr2": len(all_edges_g2),
            "common_edges_count": len(common_edges),
            "uncommon_edges_amr1_count": len(uncommon_edges_g1),
            "uncommon_edges_amr2_count": len(uncommon_edges_g2)
        }
    }


def test_amr_parsing(file_path):
    """Test function to debug AMR file parsing"""
    print(f"=== Testing AMR file: {file_path} ===")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    print(f"First 200 chars: {repr(content[:200])}")
    print(f"Last 200 chars: {repr(content[-200:])}")
    
    # Test with RawReader
    reader = RawReader()
    try:
        triples = reader._string2graph(content)
        print(f"Successfully parsed! Found {len(triples)} triples")
        print(f"First few triples: {triples[:3]}")
        return True
    except Exception as e:
        print(f"Parse failed: {e}")
        return False


def main():
    p = argparse.ArgumentParser(description="Auto‐generate alignment.json with uncommon nodes/edges")
    p.add_argument("--amr1",   required=True, help="First AMR file")
    p.add_argument("--amr2",   required=True, help="Second AMR file")
    p.add_argument("--output", default="alignment.json", help="Output JSON path")
    p.add_argument("--verbose", "-v", action="store_true", help="Show detailed statistics")
    p.add_argument("--debug", action="store_true", help="Show debug information for file parsing")
    p.add_argument("--test-parse", action="store_true", help="Test parsing only, don't compare")
    args = p.parse_args()

    if args.test_parse:
        print("Testing file parsing...")
        success1 = test_amr_parsing(args.amr1)
        success2 = test_amr_parsing(args.amr2)
        return 0 if (success1 and success2) else 1

    try:
        # Read files with error handling
        with open(args.amr1, encoding="utf-8") as f:
            s1 = f.read().strip()
        with open(args.amr2, encoding="utf-8") as f:
            s2 = f.read().strip()
        
        if args.debug:
            print(f"=== Debug: File Contents ===")
            print(f"AMR1 first 200 chars: {s1[:200]}...")
            print(f"AMR2 first 200 chars: {s2[:200]}...")
            print("=" * 40)

        alignment = compare_amr(s1, s2)
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(alignment, f, indent=2)

        print(f"Wrote alignment to {args.output}")
        
        # Print statistics
        stats = alignment["statistics"]
        print(f"\n=== Alignment Statistics ===")
        print(f"Common nodes: {stats['common_nodes_count']}")
        print(f"Common edges: {stats['common_edges_count']}")
        print(f"AMR1 unique nodes: {stats['uncommon_nodes_amr1_count']}")
        print(f"AMR2 unique nodes: {stats['uncommon_nodes_amr2_count']}")
        print(f"AMR1 unique edges: {stats['uncommon_edges_amr1_count']}")
        print(f"AMR2 unique edges: {stats['uncommon_edges_amr2_count']}")
        
        if args.verbose:
            print(f"\n=== Detailed Information ===")
            if alignment["uncommon_nodes"]["amr1_only"]:
                print(f"AMR1 unique nodes: {alignment['uncommon_nodes']['amr1_only']}")
            if alignment["uncommon_nodes"]["amr2_only"]:
                print(f"AMR2 unique nodes: {alignment['uncommon_nodes']['amr2_only']}")
            if alignment["uncommon_edges"]["amr1_only"]:
                print(f"AMR1 unique edges: {alignment['uncommon_edges']['amr1_only']}")
            if alignment["uncommon_edges"]["amr2_only"]:
                print(f"AMR2 unique edges: {alignment['uncommon_edges']['amr2_only']}")
                
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())