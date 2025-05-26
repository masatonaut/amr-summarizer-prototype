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
    for node_dot in p.get_nodes():
        name = node_dot.get_name().strip('"')
        if name not in G.nodes:
            continue
        attrs = G.nodes[name]
        if attrs.get("overlap", False):
            node_dot.set_color("red")
            node_dot.set_style("filled")
            node_dot.set_fillcolor("pink")
        else:
            node_dot.set_color("grey")
    for edge_dot in p.get_edges():
        src = edge_dot.get_source().strip('"')
        dst = edge_dot.get_destination().strip('"')

        if not G.has_edge(src, dst):
            continue
        edge_attributes = G.edges[src, dst]

        if edge_attributes.get("overlap", False):
            edge_dot.set_color("red")
            edge_dot.set_penwidth("2")
        else:
            edge_dot.set_color("grey")
            edge_dot.set_penwidth("1")
    svg_data_bytes = p.create(format="svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_data_bytes.decode("utf-8"))
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
