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
    # Load the default stog model (this may take some time on the first call).
    stog = amrlib.load_stog_model()
    graphs = stog.parse_sents([text])
    return graphs[0]  # Return the first (and usually only) AMR string.

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

    # Create a Graphviz Digraph with some layout and style options
    dot = graphviz.Digraph(
        format='svg',
        engine='dot',  # You can try "neato" or "fdp" as well
        node_attr={
            "shape": "ellipse",
            "fontsize": "12",
            "color": "#3aafa9",
            "style": "filled",
            "fillcolor": "#2b7a78"
        },
        edge_attr={
            "fontsize": "10",
            "color": "#17252a"
        }
    )
    # Optional layout tweaks
    dot.graph_attr["rankdir"] = "LR"
    dot.graph_attr["overlap"] = "false"

    # 1) Collect all variables and their concepts (from :instance triples)
    var_to_label = {}
    for var, role, concept in graph.instances():
        # For each variable, label with "var / concept" to distinguish repeated references
        node_label = f"{var} / {concept}"
        var_to_label[var] = node_label
        dot.node(var, node_label)

    # 2) Add edges for all other triples
    for src, role, tgt in graph.triples:
        # Skip :instance since we already handled them
        if role == ":instance":
            continue

        # If the target is another variable, link them directly
        if tgt in var_to_label:
            dot.edge(src, tgt, label=role)
        else:
            # Otherwise, create an attribute "box" node for the literal or string
            short_label = tgt.strip('"')  # remove surrounding quotes if present
            attr_node = f"{src}_{role}_{hash(tgt)}"
            dot.node(attr_node,
                     label=short_label,
                     shape="box",
                     style="rounded,filled",
                     fillcolor="#fe6f5e",
                     fontsize="10")
            dot.edge(src, attr_node, label=role)

    # Generate the SVG as a string
    svg_bytes = dot.pipe(format='svg')
    svg_str = svg_bytes.decode('utf-8')
    return svg_str
