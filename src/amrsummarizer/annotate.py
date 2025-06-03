import json
from typing import Dict, List, Set


def annotate_overlap(g1, g2, alignment_path: str):
    """
    Annotate NetworkX graphs g1 and g2 with overlap and uncommon information
    based on the alignment JSON file.
    
    Adds the following attributes to nodes and edges:
    - 'overlap': True if the element is common between both graphs
    - 'uncommon': True if the element is unique to this graph
    """
    # Load alignment data
    with open(alignment_path, 'r', encoding='utf-8') as f:
        alignment = json.load(f)
    
    # Extract alignment information
    common_nodes = alignment.get('common_nodes', [])
    common_edges = alignment.get('common_edges', [])
    uncommon_nodes = alignment.get('uncommon_nodes', {})
    uncommon_edges = alignment.get('uncommon_edges', {})
    
    # Convert to sets for faster lookup
    common_nodes_g1: Set[str] = {pair[0] for pair in common_nodes}
    common_nodes_g2: Set[str] = {pair[1] for pair in common_nodes}
    
    uncommon_nodes_g1: Set[str] = set(uncommon_nodes.get('amr1_only', []))
    uncommon_nodes_g2: Set[str] = set(uncommon_nodes.get('amr2_only', []))
    
    # Convert edge format for lookup: [[src, tgt, role], ...] -> {(src, tgt, role), ...}
    common_edges_g1: Set[tuple] = {(edge[0][0], edge[0][1], edge[0][2]) for edge in common_edges}
    common_edges_g2: Set[tuple] = {(edge[1][0], edge[1][1], edge[1][2]) for edge in common_edges}
    
    uncommon_edges_g1: Set[tuple] = {(edge[0], edge[1], edge[2]) for edge in uncommon_edges.get('amr1_only', [])}
    uncommon_edges_g2: Set[tuple] = {(edge[0], edge[1], edge[2]) for edge in uncommon_edges.get('amr2_only', [])}
    
    print(f"=== Annotation Debug ===")
    print(f"G1 nodes: {list(g1.nodes())}")
    print(f"G2 nodes: {list(g2.nodes())}")
    print(f"Common nodes G1: {common_nodes_g1}")
    print(f"Common nodes G2: {common_nodes_g2}")
    print(f"Uncommon nodes G1: {uncommon_nodes_g1}")
    print(f"Uncommon nodes G2: {uncommon_nodes_g2}")
    
    # Annotate nodes in g1
    for node in g1.nodes():
        if node in common_nodes_g1:
            g1.nodes[node]['overlap'] = True
            g1.nodes[node]['uncommon'] = False
            print(f"G1 node '{node}' -> OVERLAP (red)")
        elif node in uncommon_nodes_g1:
            g1.nodes[node]['overlap'] = False
            g1.nodes[node]['uncommon'] = True
            print(f"G1 node '{node}' -> UNCOMMON (blue)")
        else:
            g1.nodes[node]['overlap'] = False
            g1.nodes[node]['uncommon'] = False
            print(f"G1 node '{node}' -> DEFAULT (grey)")
    
    # Annotate nodes in g2
    for node in g2.nodes():
        if node in common_nodes_g2:
            g2.nodes[node]['overlap'] = True
            g2.nodes[node]['uncommon'] = False
            print(f"G2 node '{node}' -> OVERLAP (red)")
        elif node in uncommon_nodes_g2:
            g2.nodes[node]['overlap'] = False
            g2.nodes[node]['uncommon'] = True
            print(f"G2 node '{node}' -> UNCOMMON (blue)")
        else:
            g2.nodes[node]['overlap'] = False
            g2.nodes[node]['uncommon'] = False
            print(f"G2 node '{node}' -> DEFAULT (grey)")
    
    # Annotate edges in g1
    print(f"\n=== G1 Edge Annotation ===")
    for src, tgt in g1.edges():
        # Get edge attributes to find the role
        edge_attrs = g1.edges[src, tgt]
        role = edge_attrs.get('role', edge_attrs.get('label', ''))
        
        edge_tuple = (src, tgt, role)
        
        if edge_tuple in common_edges_g1:
            g1.edges[src, tgt]['overlap'] = True
            g1.edges[src, tgt]['uncommon'] = False
            print(f"G1 edge {edge_tuple} -> OVERLAP (red)")
        elif edge_tuple in uncommon_edges_g1:
            g1.edges[src, tgt]['overlap'] = False
            g1.edges[src, tgt]['uncommon'] = True
            print(f"G1 edge {edge_tuple} -> UNCOMMON (blue)")
        else:
            g1.edges[src, tgt]['overlap'] = False
            g1.edges[src, tgt]['uncommon'] = False
            print(f"G1 edge {edge_tuple} -> DEFAULT (grey)")
    
    # Annotate edges in g2
    print(f"\n=== G2 Edge Annotation ===")
    for src, tgt in g2.edges():
        # Get edge attributes to find the role
        edge_attrs = g2.edges[src, tgt]
        role = edge_attrs.get('role', edge_attrs.get('label', ''))
        
        edge_tuple = (src, tgt, role)
        
        if edge_tuple in common_edges_g2:
            g2.edges[src, tgt]['overlap'] = True
            g2.edges[src, tgt]['uncommon'] = False
            print(f"G2 edge {edge_tuple} -> OVERLAP (red)")
        elif edge_tuple in uncommon_edges_g2:
            g2.edges[src, tgt]['overlap'] = False
            g2.edges[src, tgt]['uncommon'] = True
            print(f"G2 edge {edge_tuple} -> UNCOMMON (blue)")
        else:
            g2.edges[src, tgt]['overlap'] = False
            g2.edges[src, tgt]['uncommon'] = False
            print(f"G2 edge {edge_tuple} -> DEFAULT (grey)")
    
    print(f"=== Annotation Complete ===\n")
    
    # Annotate edges in g1
    for src, tgt in g1.edges():
        # Get edge attributes to find the role
        edge_attrs = g1.edges[src, tgt]
        role = edge_attrs.get('role', edge_attrs.get('label', ''))
        
        edge_tuple = (src, tgt, role)
        
        if edge_tuple in common_edges_g1:
            g1.edges[src, tgt]['overlap'] = True
            g1.edges[src, tgt]['uncommon'] = False
        elif edge_tuple in uncommon_edges_g1:
            g1.edges[src, tgt]['overlap'] = False
            g1.edges[src, tgt]['uncommon'] = True
        else:
            g1.edges[src, tgt]['overlap'] = False
            g1.edges[src, tgt]['uncommon'] = False
    
    # Annotate edges in g2
    for src, tgt in g2.edges():
        # Get edge attributes to find the role
        edge_attrs = g2.edges[src, tgt]
        role = edge_attrs.get('role', edge_attrs.get('label', ''))
        
        edge_tuple = (src, tgt, role)
        
        if edge_tuple in common_edges_g2:
            g2.edges[src, tgt]['overlap'] = True
            g2.edges[src, tgt]['uncommon'] = False
        elif edge_tuple in uncommon_edges_g2:
            g2.edges[src, tgt]['overlap'] = False
            g2.edges[src, tgt]['uncommon'] = True
        else:
            g2.edges[src, tgt]['overlap'] = False
            g2.edges[src, tgt]['uncommon'] = False


def print_annotation_summary(g1, g2, graph1_name="AMR1", graph2_name="AMR2"):
    """
    Print a summary of the annotation results for debugging purposes.
    """
    def count_attributes(graph, attr_name):
        nodes_with_attr = sum(1 for _, attrs in graph.nodes(data=True) if attrs.get(attr_name, False))
        edges_with_attr = sum(1 for _, _, attrs in graph.edges(data=True) if attrs.get(attr_name, False))
        return nodes_with_attr, edges_with_attr
    
    print(f"\n=== Annotation Summary ===")
    
    # Count overlapping elements
    g1_overlap_nodes, g1_overlap_edges = count_attributes(g1, 'overlap')
    g2_overlap_nodes, g2_overlap_edges = count_attributes(g2, 'overlap')
    
    print(f"{graph1_name}: {g1_overlap_nodes} overlapping nodes, {g1_overlap_edges} overlapping edges")
    print(f"{graph2_name}: {g2_overlap_nodes} overlapping nodes, {g2_overlap_edges} overlapping edges")
    
    # Count uncommon elements
    g1_uncommon_nodes, g1_uncommon_edges = count_attributes(g1, 'uncommon')
    g2_uncommon_nodes, g2_uncommon_edges = count_attributes(g2, 'uncommon')
    
    print(f"{graph1_name}: {g1_uncommon_nodes} unique nodes, {g1_uncommon_edges} unique edges")
    print(f"{graph2_name}: {g2_uncommon_nodes} unique nodes, {g2_uncommon_edges} unique edges")


def test_annotation():
    """
    Test function for debugging annotation logic.
    """
    # This would require actual graph objects to test
    print("Annotation test function - requires graph objects for testing")


if __name__ == "__main__":
    test_annotation()