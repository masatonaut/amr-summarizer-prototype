# backend/annotate.py

import json
import networkx as nx


def annotate_overlap(
    G1: nx.DiGraph,
    G2: nx.DiGraph,
    alignment_path: str
) -> None:
    """
    Load alignment data from a JSON file and mark
    overlapping nodes/edges in G1 and G2.

    The JSON alignment file is expected to have this structure:
    {
        "common_nodes": [
            ["node_id_in_graph1", "node_id_in_graph2"],
            ...
        ],
        "common_edges": [
            [
                ["src1", "tgt1", "role1"],
                ["src2", "tgt2", "role2"]
            ],
            ...
        ]
    }

    After calling this function, each node and edge in G1/G2
    will have an 'overlap' boolean attribute.
    """
    # 1) Read alignment JSON
    with open(alignment_path, "r", encoding="utf-8") as f:
        align = json.load(f)

    # 2) Initialize all nodes/edges as non-overlap
    for G in (G1, G2):
        nx.set_node_attributes(G, False, "overlap")
        for u, v in G.edges():
            G.edges[u, v]["overlap"] = False

    # 3) Mark overlapping nodes
    for n1, n2 in align.get("common_nodes", []):
        if n1 in G1.nodes:
            G1.nodes[n1]["overlap"] = True
        if n2 in G2.nodes:
            G2.nodes[n2]["overlap"] = True

    # 4) Mark overlapping edges
    for (u1, v1, r1), (u2, v2, r2) in align.get("common_edges", []):
        if G1.has_edge(u1, v1) and G1.edges[u1, v1].get("role") == r1:
            G1.edges[u1, v1]["overlap"] = True
        if G2.has_edge(u2, v2) and G2.edges[u2, v2].get("role") == r2:
            G2.edges[u2, v2]["overlap"] = True
