import json

def _get_networkx_edge_representation(align_s, align_t, align_rel):
    """
    Convert an edge from alignment.json (surface form, e.g., with :ROLE-of)
    to its expected representation in a NetworkX graph (canonical form, e.g., :ROLE with swapped s/t).
    Returns (nx_source, nx_target, nx_relation_label).
    This function makes assumptions about how amr2nx.py stores relations and handles inverse roles.
    """
    # Check if the relation is likely an inverse role like :ARG0-of
    if isinstance(align_rel, str) and align_rel.endswith("-of") and \
       align_rel.startswith(":") and len(align_rel) > (len("-of") + 1): # Ensure it's not just ":-of"
        
        direct_role_name = align_rel[:-len("-of")] # Removes "-of"
        
        if direct_role_name.startswith(":") and len(direct_role_name) > 1:
            nx_relation = direct_role_name
            nx_source = align_t 
            nx_target = align_s 
            return nx_source, nx_target, nx_relation

    return align_s, align_t, align_rel


def annotate_overlap(g1, g2, alignment_file):
    """
    Annotates nodes and edges in NetworkX graphs g1 and g2 with 'overlap':True
    if they are found to be common based on the alignment_file.
    Assumes g1 and g2 are NetworkX graphs (can be DiGraph or MultiDiGraph)
    and that edge relation labels are stored in an attribute named 'role'
    by the amr2nx.py script.
    """
    with open(alignment_file, 'r', encoding='utf-8') as f:
        alignment = json.load(f)

    # Initialize 'overlap' attribute to False for all nodes
    for node_id in g1.nodes():
        g1.nodes[node_id]['overlap'] = False
    for node_id in g2.nodes():
        g2.nodes[node_id]['overlap'] = False

    # Initialize 'overlap' attribute to False for all edges
    if g1.is_multigraph():
        for u, v, key, data_dict in g1.edges(data=True, keys=True):
            data_dict['overlap'] = False
    else:
        for u, v, data_dict in g1.edges(data=True):
            data_dict['overlap'] = False

    if g2.is_multigraph():
        for u, v, key, data_dict in g2.edges(data=True, keys=True):
            data_dict['overlap'] = False
    else:
        for u, v, data_dict in g2.edges(data=True):
            data_dict['overlap'] = False
    
    # Annotate common nodes
    common_nodes_list = alignment.get('common_nodes', [])
    for node_pair in common_nodes_list:
        if len(node_pair) >= 2:
            node1_align_var, node2_align_var = node_pair[0], node_pair[1]
            if node1_align_var in g1.nodes:
                g1.nodes[node1_align_var]['overlap'] = True
            if node2_align_var in g2.nodes:
                g2.nodes[node2_align_var]['overlap'] = True

    # Annotate common edges
    common_edges_list = alignment.get('common_edges', [])
    for edge_pair_data in common_edges_list:
        if len(edge_pair_data) >= 2:
            edge_g1_align_data = edge_pair_data[0]
            edge_g2_align_data = edge_pair_data[1]
            
            if len(edge_g1_align_data) == 3 and len(edge_g2_align_data) == 3:
                s1_align, t1_align, r1_align_surface = edge_g1_align_data
                s2_align, t2_align, r2_align_surface = edge_g2_align_data
                
                # Convert alignment representation to NetworkX representation
                nx_s1, nx_t1, nx_r1 = _get_networkx_edge_representation(
                    s1_align, t1_align, r1_align_surface
                )
                nx_s2, nx_t2, nx_r2 = _get_networkx_edge_representation(
                    s2_align, t2_align, r2_align_surface
                )
                
                # Mark edges as overlapping in both graphs
                _mark_edge_overlap(g1, nx_s1, nx_t1, nx_r1)
                _mark_edge_overlap(g2, nx_s2, nx_t2, nx_r2)


def _mark_edge_overlap(graph, source, target, role):
    """
    Mark an edge as overlapping in the given graph.
    Handles both MultiDiGraph and DiGraph cases.
    """
    if not graph.has_edge(source, target):
        return
        
    if graph.is_multigraph():
        # For MultiDiGraph, find edges with matching role
        edge_data_dict = graph.get_edge_data(source, target)
        for key, data in edge_data_dict.items():
            if data.get('role') == role:
                data['overlap'] = True
    else:
        # For DiGraph, mark the single edge
        edge_data = graph.get_edge_data(source, target)
        if edge_data and edge_data.get('role') == role:
            edge_data['overlap'] = True