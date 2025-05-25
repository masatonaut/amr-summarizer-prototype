import argparse
from amr2nx import load_amr_graph
from annotate import annotate_overlap
from networkx.drawing.nx_pydot import to_pydot


def render_graph(G, output_path):
    """
    Render a single AMR graph G (with 'overlap' attributes)
    to an SVG file at output_path.
    """
    p = to_pydot(G)
    # style nodes
    for node in p.get_nodes():
        name = node.get_name().strip('"')
        attrs = G.nodes[name]
        if attrs.get("overlap", False):
            node.set_color("red")
            node.set_style("filled")
            node.set_fillcolor("pink")
        else:
            node.set_color("grey")
    # style edges
    for edge in p.get_edges():
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        eattr = G.edges[src, dst]
        if eattr.get("overlap", False):
            edge.set_color("red")
            edge.set_penwidth("2")
        else:
            edge.set_color("grey")
            edge.set_penwidth("1")
    # produce SVG via Graphviz
    svg_data = p.create(format="svg")
    with open(output_path, "wb") as f:
        f.write(svg_data)
    print(f"Wrote {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize two AMR graphs highlighting overlapping parts"
    )
    parser.add_argument("--amr1", required=True, help="path to first AMR (.amr) file")
    parser.add_argument("--amr2", required=True, help="path to second AMR file")
    parser.add_argument("--alignment", required=True, help="path to alignment.json")
    parser.add_argument("--out1", default="g1.svg", help="output SVG for first graph")
    parser.add_argument("--out2", default="g2.svg", help="output SVG for second graph")
    args = parser.parse_args()

    # load & annotate
    g1 = load_amr_graph(open(args.amr1, encoding="utf-8").read())
    g2 = load_amr_graph(open(args.amr2, encoding="utf-8").read())
    annotate_overlap(g1, g2, args.alignment)

    # render both
    render_graph(g1, args.out1)
    render_graph(g2, args.out2)


if __name__ == "__main__":
    main()
