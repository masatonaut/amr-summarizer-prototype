import argparse
from amr2nx import load_amr_graph
from annotate import annotate_overlap
from networkx.drawing.nx_pydot import to_pydot


def render_graph(G, output_path, graph_name="AMR"):
    """
    Render a single AMR graph G (with 'overlap' and 'uncommon' attributes)
    to an SVG file at output_path.
    
    Color scheme:
    - Red/Pink: Common/overlapping elements
    - Blue/Light Blue: Uncommon elements (unique to this graph)
    - Grey: Default/other elements
    """
    p = to_pydot(G)
    
    # Set graph title and compact layout options
    p.set_label(f"{graph_name}\\nRed: Common, Blue: Unique, Grey: Other")
    p.set_labelloc("t")
    p.set_fontsize("12")
    
    # Settings to ensure large, clear graph display
    p.set_rankdir("TB")         # Top to Bottom layout
    p.set_size("")              # Remove size constraint
    p.set_dpi("96")             # Higher DPI for clarity
    p.set_ratio("auto")         # Auto ratio to fit content
    p.set_margin("0.8")         # Large margin
    p.set_splines("true")       # Smooth lines
    p.set_overlap("false")      # Prevent overlap
    p.set_sep("1.0")            # Large separation
    p.set_nodesep("1.2")        # Large node separation
    p.set_ranksep("1.5")        # Large rank separation
    p.set_concentrate("false")  # Don't merge edges
    p.set_pack("false")         # Don't pack
    p.set_center("true")        # Center the graph
    
    # Debug: count nodes by type
    overlap_nodes = []
    uncommon_nodes = []
    default_nodes = []
    
    # Style nodes with compact settings
    for node_dot in p.get_nodes():
        name = node_dot.get_name().strip('"')
        if name not in G.nodes:
            continue
        attrs = G.nodes[name]
        
        # Large, readable node attributes
        node_dot.set_fontsize("14")
        node_dot.set_height("0.6")
        node_dot.set_width("1.2")
        node_dot.set_shape("ellipse")
        node_dot.set_margin("0.15,0.08")  # Generous margins
        
        if attrs.get("overlap", False):
            # Common nodes - red/pink
            node_dot.set_color("red")
            node_dot.set_style("filled")
            node_dot.set_fillcolor("pink")
            node_dot.set_penwidth("1")
            overlap_nodes.append(name)
        elif attrs.get("uncommon", False):
            # Uncommon nodes - blue/light blue
            node_dot.set_color("blue")
            node_dot.set_style("filled") 
            node_dot.set_fillcolor("lightblue")
            node_dot.set_penwidth("1")
            uncommon_nodes.append(name)
        else:
            # Default nodes - grey
            node_dot.set_color("grey")
            node_dot.set_style("filled")
            node_dot.set_fillcolor("lightgrey")
            default_nodes.append(name)
    
    # Debug: count edges by type
    overlap_edges = []
    uncommon_edges = []
    default_edges = []
    
    # Style edges with compact settings
    for edge_dot in p.get_edges():
        src = edge_dot.get_source().strip('"')
        dst = edge_dot.get_destination().strip('"')

        if not G.has_edge(src, dst):
            continue
        edge_attributes = G.edges[src, dst]
        edge_id = f"{src}->{dst}"

        # Large, readable edge attributes
        edge_dot.set_fontsize("10")
        edge_dot.set_arrowsize("0.8")
        edge_dot.set_minlen("1.5")  # Longer edges for clarity
        
        if edge_attributes.get("overlap", False):
            # Common edges - red
            edge_dot.set_color("red")
            edge_dot.set_penwidth("2")
            edge_dot.set_style("solid")
            overlap_edges.append(edge_id)
        elif edge_attributes.get("uncommon", False):
            # Uncommon edges - blue
            edge_dot.set_color("blue")
            edge_dot.set_penwidth("2")
            edge_dot.set_style("solid")
            uncommon_edges.append(edge_id)
        else:
            # Default edges - grey
            edge_dot.set_color("grey")
            edge_dot.set_penwidth("1")
            edge_dot.set_style("solid")
            default_edges.append(edge_id)
    
    # Generate SVG that shows the complete graph
    try:
        svg_data_bytes = p.create(format="svg")
        svg_content = svg_data_bytes.decode("utf-8")
        
        # Ensure SVG is responsive and shows full content
        import re
        
        # Extract the original viewBox or create one from width/height
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        width_match = re.search(r'width="(\d+(?:\.\d+)?)(?:pt|px)?"', svg_content)
        height_match = re.search(r'height="(\d+(?:\.\d+)?)(?:pt|px)?"', svg_content)
        
        if width_match and height_match:
            width = float(width_match.group(1))
            height = float(height_match.group(1))
            
            # Use existing viewBox or create one that shows full content
            if viewbox_match:
                viewbox = viewbox_match.group(1)
            else:
                viewbox = f'0 0 {width} {height}'
            
            # Replace SVG tag to ensure full visibility with no size constraints
            new_svg_tag = f'<svg viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%; max-width: none; max-height: none;">'
            
            svg_content = re.sub(r'<svg[^>]*>', new_svg_tag, svg_content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
    except Exception as e:
        print(f"Error generating SVG: {e}")
        # Fallback to basic generation
        svg_data_bytes = p.create(format="svg")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_data_bytes.decode("utf-8"))
    
    print(f"Wrote {output_path}")
    print(f"  {graph_name} node colors: Red={len(overlap_nodes)}, Blue={len(uncommon_nodes)}, Grey={len(default_nodes)}")
    print(f"  {graph_name} edge colors: Red={len(overlap_edges)}, Blue={len(uncommon_edges)}, Grey={len(default_edges)}")
    
    if uncommon_nodes:
        print(f"  {graph_name} blue nodes: {uncommon_nodes}")
    if uncommon_edges:
        print(f"  {graph_name} blue edges: {uncommon_edges}")


def visualize_overlap(amr1_path, amr2_path, alignment_path, out1_path, out2_path):
    """
    Main function to visualize AMR overlap with uncommon elements highlighted.
    This function can be called from other modules.
    """
    print(f"Loading AMR files...")
    print(f"  AMR1: {amr1_path}")
    print(f"  AMR2: {amr2_path}")
    print(f"  Alignment: {alignment_path}")
    
    # Load AMR graphs
    try:
        with open(amr1_path, encoding="utf-8") as f:
            amr1_content = f.read()
        print(f"AMR1 file read successfully, length: {len(amr1_content)}")
        
        with open(amr2_path, encoding="utf-8") as f:
            amr2_content = f.read()
        print(f"AMR2 file read successfully, length: {len(amr2_content)}")
        
        print("Converting AMR1 to graph...")
        g1 = load_amr_graph(amr1_content)
        print(f"AMR1 graph: {len(g1.nodes())} nodes, {len(g1.edges())} edges")
        
        print("Converting AMR2 to graph...")
        g2 = load_amr_graph(amr2_content)
        print(f"AMR2 graph: {len(g2.nodes())} nodes, {len(g2.edges())} edges")
        
        # Annotate with overlap and uncommon information
        print("Annotating overlap information...")
        annotate_overlap(g1, g2, alignment_path)
        
        # Render both graphs
        print("Rendering graphs...")
        render_graph(g1, out1_path, "AMR 1")
        render_graph(g2, out2_path, "AMR 2")
        
        return out1_path, out2_path
        
    except Exception as e:
        print(f"Error in visualize_overlap: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Visualize two AMR graphs highlighting overlapping and unique parts"
    )
    parser.add_argument("--amr1", required=True, help="Path to first AMR (.amr) file")
    parser.add_argument("--amr2", required=True, help="Path to second AMR file")
    parser.add_argument("--alignment", required=True, help="Path to alignment.json")
    parser.add_argument("--out1", default="g1.svg", help="Output SVG for first graph")
    parser.add_argument("--out2", default="g2.svg", help="Output SVG for second graph")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Loading AMR files: {args.amr1}, {args.amr2}")
            print(f"Using alignment: {args.alignment}")
        
        # Visualize overlap
        out1, out2 = visualize_overlap(args.amr1, args.amr2, args.alignment, args.out1, args.out2)
        
        print(f"\nVisualization complete:")
        print(f"  AMR 1 visualization: {out1}")
        print(f"  AMR 2 visualization: {out2}")
        print(f"\nColor legend:")
        print(f"  🔴 Red/Pink: Common elements (present in both AMRs)")
        print(f"  🔵 Blue/Light Blue: Unique elements (present only in this AMR)")
        print(f"  ⚫ Grey: Other elements")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return 1
    except Exception as e:
        print(f"Error during visualization: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())