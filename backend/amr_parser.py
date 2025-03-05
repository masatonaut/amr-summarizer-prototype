import amrlib
import penman
import graphviz
from collections import Counter
from penman import constant

def parse_amr(text: str) -> str:
    """
    Parse the input text into an AMR graph using amrlib's public API.

    Parameters:
        text (str): The input sentence or text to parse.
    
    Returns:
        str: The AMR graph representation as a Penman string.
    """
    # Load the default stog model (this may take some time on the first call)
    stog = amrlib.load_stog_model()
    graphs = stog.parse_sents([text])
    return graphs[0]

def amr_to_svg(amr_str: str) -> str:
    """
    Convert a Penman AMR string into an SVG image using Graphviz.

    Parameters:
        amr_str (str): The AMR graph representation as a Penman string.
    
    Returns:
        str: The SVG representation of the AMR graph.
    """
    # Decode the AMR string into a penman.Graph object
    graph = penman.decode(amr_str)

    # Create a Graphviz Digraph object with basic node and edge attributes
    dot = graphviz.Digraph(format='svg', node_attr={
        "shape": "ellipse", 
        "fontsize": "12", 
        "color": "#3aafa9", 
        "style": "filled", 
        "fillcolor": "#2b7a78"
    }, edge_attr={"fontsize": "10", "color": "#17252a"})

    # Add nodes for each instance triple (triples with ':instance')
    for var, role, label in graph.instances():
        dot.node(var, label)

    # Add edges for all other triples
    for src, role, tgt in graph.triples:
        if role == ":instance":
            continue  # Skip instance declarations
        # If the target is an instance, add an edge directly
        if any(triple[0] == tgt and triple[1] == ":instance" for triple in graph.triples):
            dot.edge(src, tgt, label=role)
        else:
            # Otherwise, create an auxiliary node for the attribute value
            attr_node = f"{src}_{role}_{tgt}"
            dot.node(attr_node, label=tgt, shape="box", style="rounded,filled", fillcolor="#fe6f5e")
            dot.edge(src, attr_node, label=role)

    # Generate and return the SVG string
    svg_bytes = dot.pipe(format='svg')
    svg_str = svg_bytes.decode('utf-8')
    return svg_str
