import amrlib
import penman
import graphviz
import torch
import gc
from collections import Counter
from penman import constant

def parse_amr(text: str) -> str:
    """
    Parse the input text into an AMR graph using amrlib's public API.

    Parameters:
        text (str): The input sentence or text to parse.
    
    Returns:
        str: The raw AMR string in Penman notation.
    """
    # Load the default stog model (this may take time on the first call)
    stog = amrlib.load_stog_model(model_dir="/mnt/idms/home/botondbarta/models/model_parse_xfm_bart_large-v0_1_0")
    graphs = stog.parse_sents([text])
    stog.model.to('cpu')
    del stog
    gc.collect()
    torch.cuda.empty_cache() 
    return graphs[0]

def amr_to_svg(amr_str: str) -> str:
    """
    Convert a Penman AMR string into an SVG image using Graphviz,
    with variable renaming for repeated instances.

    Parameters:
        amr_str (str): The AMR graph in Penman notation.
    
    Returns:
        str: The SVG representation of the AMR graph.
    """
    # Decode the AMR string into a penman.Graph object
    graph = penman.decode(amr_str)

    # Optional: Replace numeric attribute values with placeholders
    anon_map = {}
    attributes = []
    for src, role, tgt in graph.attributes():
        if constant.type(tgt) in (constant.INTEGER, constant.FLOAT):
            anon_val = f'number_{len(anon_map)}'
            anon_map[anon_val] = tgt
            tgt = anon_val
        attributes.append((src, role, tgt))
    new_graph = penman.Graph(graph.instances() + graph.edges() + attributes)

    # Create a Graphviz Digraph object with custom styling
    dot = graphviz.Digraph(
        format='svg',
        node_attr={
            "color": "#3aafa9",
            "style": "rounded,filled",
            "shape": "box",
            "fontcolor": "white"
        },
        edge_attr={
            "fontsize": "10",
            "color": "#17252a"
        }
    )

    # Count occurrences of instance labels for renaming duplicates
    instance_labels = [t[2] for t in new_graph.triples if t[1] == ":instance"]
    label_counts = Counter(instance_labels)

    # Build a dictionary mapping variable to a unique display label
    var_to_label = {}
    occurrence_counter = Counter()
    for var, role, lbl in new_graph.instances():
        if label_counts[lbl] > 1:
            occurrence_counter[lbl] += 1
            var_to_label[var] = f"{lbl} ({occurrence_counter[lbl]})"
        else:
            var_to_label[var] = lbl

    def get_node_name(var: str) -> str:
        return var_to_label.get(var, var)

    # Add nodes (from :instance triples) and edges for all other triples
    for src, role, tgt in new_graph.triples:
        if role == ":instance":
            dot.node(src, get_node_name(src))
        else:
            if tgt in var_to_label:
                dot.edge(src, tgt, label=role)
            else:
                attr_node = f"{src}_{role}_{tgt}"
                display_val = anon_map.get(tgt, tgt)
                dot.node(attr_node, label=display_val, shape="ellipse", style="filled,rounded", fillcolor="#fe6f5e", fontcolor="white")
                dot.edge(src, attr_node, label=role)

    svg_bytes = dot.pipe(format='svg')
    svg_str = svg_bytes.decode('utf-8')
    return svg_str
