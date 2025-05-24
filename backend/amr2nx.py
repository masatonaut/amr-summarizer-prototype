import penman
import networkx as nx


def load_amr_graph(penman_str: str) -> nx.DiGraph:
    """
    Convert a PENMAN-formatted AMR string into a NetworkX DiGraph.

    Node attributes:
        - label: the concept name (from :instance triples)
        - is_constant (optional): True if the node represents a constant literal

    Edge attributes:
        - role: the relation label (e.g. ':ARG0', ':mod', etc.)
    """
    # 1) Decode the PENMAN string into a penman.Graph
    graph = penman.decode(penman_str)

    # 2) Create an empty directed graph
    G = nx.DiGraph()

    # 3) Add nodes for all instance triples
    for source, role, target in graph.triples:
        if role == ":instance":
            # source is the variable name (e.g. 'x'), target is the concept (e.g. 'cat')
            G.add_node(source, label=target)

    # 4) Add edges for all non-instance triples
    for source, role, target in graph.triples:
        if role != ":instance":
            # If target is not already a node (i.e. a constant), add it as such
            if target not in G:
                G.add_node(target, label=target, is_constant=True)
            # Add a directed edge with the role as an attribute
            G.add_edge(source, target, role=role)

    return G


if __name__ == "__main__":
    # Simple CLI for manual testing:
    # python amr2nx.py path/to/sample.amr
    import sys

    if len(sys.argv) != 2:
        print("Usage: python amr2nx.py <path_to_amr_file>")
        sys.exit(1)

    text = open(sys.argv[1], encoding="utf-8").read()
    G = load_amr_graph(text)

    print("=== Nodes ===")
    for n, attrs in G.nodes(data=True):
        print(f"{n}: {attrs}")

    print("\n=== Edges ===")
    for u, v, attrs in G.edges(data=True):
        print(f"{u} -> {v}: {attrs}")
