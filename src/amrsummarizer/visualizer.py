#!/usr/bin/env python3
"""
Complete AMR Visualizer - Generate both individual and union graphs
"""

import argparse
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from amr2nx import load_amr_graph
from annotate import annotate_overlap
import networkx as nx
import json
import math

def render_individual_graph(G, output_path, graph_name="AMR"):
    """Render individual AMR graph with hierarchical layout"""
    
    # Count nodes by type
    overlap_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get('overlap', False)]
    uncommon_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get('uncommon', False)]
    default_nodes = [n for n, attrs in G.nodes(data=True) if not attrs.get('overlap', False) and not attrs.get('uncommon', False)]
    
    overlap_edges = [(s, d) for s, d, attrs in G.edges(data=True) if attrs.get('overlap', False)]
    uncommon_edges = [(s, d) for s, d, attrs in G.edges(data=True) if attrs.get('uncommon', False)]
    default_edges = [(s, d) for s, d, attrs in G.edges(data=True) if not attrs.get('overlap', False) and not attrs.get('uncommon', False)]
    
    width, height = 1200, 900
    nodes = list(G.nodes())
    
    if not nodes:
        print(f"WARNING: {graph_name} has no nodes!")
        return
    
    # Get hierarchical layout
    positions = calculate_hierarchical_positions(G, width, height)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background: white; border: 1px solid #ddd;">
  <title>{graph_name}</title>
  
  <!-- Graph Title -->
  <text x="{width//2}" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold">
    {graph_name} - Red: Common, Blue: Unique, Grey: Other
  </text>
  
  <!-- Statistics -->
  <text x="20" y="60" font-family="Arial" font-size="12" fill="#666">
    Nodes: {len(nodes)} | Overlap: {len(overlap_nodes)} | Unique: {len(uncommon_nodes)} | Other: {len(default_nodes)}
  </text>
  
  <!-- Arrow markers -->
  <defs>
    <marker id="arrowhead-red" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="red"/>
    </marker>
    <marker id="arrowhead-blue" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="blue"/>
    </marker>
    <marker id="arrowhead-grey" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="grey"/>
    </marker>
  </defs>
  
  <!-- Edges -->
'''
    
    # Draw edges
    for src, dst, attrs in G.edges(data=True):
        if src not in positions or dst not in positions:
            continue
            
        x1, y1 = positions[src]['x'], positions[src]['y']
        x2, y2 = positions[dst]['x'], positions[dst]['y']
        
        if attrs.get('overlap', False):
            color = 'red'
            stroke_width = '3'
            opacity = '1.0'
        elif attrs.get('uncommon', False):
            color = 'blue' 
            stroke_width = '2'
            opacity = '0.8'
        else:
            color = 'grey'
            stroke_width = '1'
            opacity = '0.6'
            
        label = attrs.get('role', attrs.get('label', ''))
        if label.startswith(':'):
            label = label[1:]
        
        label_x = x1 + 0.3 * (x2 - x1)
        label_y = y1 + 0.3 * (y2 - y1) - 5
        
        svg_content += f'''
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
        stroke="{color}" stroke-width="{stroke_width}" 
        marker-end="url(#arrowhead-{color})" opacity="{opacity}"/>
  <text x="{label_x}" y="{label_y}" font-family="Arial" font-size="9" 
        fill="{color}" font-weight="bold" opacity="0.9">{label}</text>
'''
    
    svg_content += '\n  <!-- Nodes -->\n'
    
    # Draw nodes
    for node, attrs in G.nodes(data=True):
        if node not in positions:
            continue
            
        x, y = positions[node]['x'], positions[node]['y']
        
        if attrs.get('overlap', False):
            fill_color = '#ffdddd'  # Light red
            stroke_color = '#cc0000'  # Dark red
            stroke_width = '3'
        elif attrs.get('uncommon', False):
            fill_color = '#ddddff'  # Light blue
            stroke_color = '#0000cc'  # Dark blue
            stroke_width = '2'
        else:
            fill_color = '#f5f5f5'  # Very light grey
            stroke_color = '#888888'  # Medium grey
            stroke_width = '1'
        
        label = attrs.get('instance', attrs.get('label', str(node)))
        is_literal = (str(node).startswith('"') or '_op' in str(node) or 
                     str(label).startswith('"') or attrs.get('literal'))
        is_concept = attrs.get('instance') and not is_literal
        
        if is_literal:
            text_width = max(60, len(str(label)) * 8)
            node_width, node_height = min(text_width, 120), 30
            clean_label = str(label).replace('"', '').strip()
            if len(clean_label) > 12:
                clean_label = clean_label[:12] + "..."
            
            svg_content += f'''
  <rect x="{x-node_width//2}" y="{y-node_height//2}" width="{node_width}" height="{node_height}" 
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" rx="8"/>
  <text x="{x}" y="{y+4}" text-anchor="middle" 
        font-family="Arial" font-size="10" font-weight="bold">{clean_label}</text>
'''
        elif is_concept:
            radius = 30
            clean_label = str(label)
            if len(clean_label) > 12:
                clean_label = clean_label[:12] + "..."
                
            svg_content += f'''
  <circle cx="{x}" cy="{y}" r="{radius}" 
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>
  <text x="{x}" y="{y+4}" text-anchor="middle" 
        font-family="Arial" font-size="11" font-weight="bold">{clean_label}</text>
'''
        else:
            radius = 20
            clean_label = str(node)
            if len(clean_label) > 8:
                clean_label = clean_label[:8] + "..."
                
            svg_content += f'''
  <circle cx="{x}" cy="{y}" r="{radius}" 
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>
  <text x="{x}" y="{y+3}" text-anchor="middle" 
        font-family="Arial" font-size="10" font-weight="bold">{clean_label}</text>
'''
    
    svg_content += '''
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ {graph_name} saved: {output_path}")
    print(f"   Node colors: Red={len(overlap_nodes)}, Blue={len(uncommon_nodes)}, Grey={len(default_nodes)}")
    print(f"   Edge colors: Red={len(overlap_edges)}, Blue={len(uncommon_edges)}, Grey={len(default_edges)}")

def calculate_hierarchical_positions(G, width, height):
    """Calculate hierarchical positions for nodes"""
    # Find root node
    root = find_root_node(G)
    if not root:
        root = list(G.nodes())[0]
    
    positions = {}
    levels = {root: 0}
    visited = {root}
    queue = [root]
    max_level = 0
    
    # BFS to assign levels
    while queue:
        current = queue.pop(0)
        current_level = levels[current]
        max_level = max(max_level, current_level)
        
        for _, child in G.edges(current):
            if child not in visited:
                visited.add(child)
                levels[child] = current_level + 1
                queue.append(child)
    
    # Add remaining nodes
    for node in G.nodes():
        if node not in levels:
            levels[node] = max_level + 1
    
    # Group by level
    level_groups = {}
    for node, level in levels.items():
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(node)
    
    # Position nodes
    margin = 80
    level_height = (height - 2 * margin) / (max_level + 1) if max_level > 0 else height // 2
    
    for level, nodes in level_groups.items():
        y = margin + level * level_height
        
        if len(nodes) == 1:
            positions[nodes[0]] = {'x': width // 2, 'y': y}
        else:
            node_width = (width - 2 * margin) / len(nodes)
            for i, node in enumerate(nodes):
                positions[node] = {
                    'x': margin + (i + 0.5) * node_width,
                    'y': y
                }
    
    return positions

def find_root_node(G):
    """Find root node based on AMR structure"""
    for node, attrs in G.nodes(data=True):
        if attrs.get('instance'):
            concept = attrs.get('instance', '')
            if any(root_concept in concept for root_concept in ['say-01', 'offer-01', 'want-01', 'believe-01']):
                return node
    
    # Fallback to first concept node
    for node, attrs in G.nodes(data=True):
        if attrs.get('instance'):
            return node
    
    return list(G.nodes())[0] if G.nodes() else None

def create_improved_union_graph(g1, g2, alignment_data):
    """Create improved union graph with better alignment detection"""
    union_graph = nx.DiGraph()
    
    # Get alignment data
    common_nodes = alignment_data.get('common_nodes', [])
    uncommon_nodes = alignment_data.get('uncommon_nodes', {})
    
    print(f"Common nodes from alignment: {len(common_nodes)}")
    print(f"AMR1 unique nodes: {len(uncommon_nodes.get('amr1_only', []))}")
    print(f"AMR2 unique nodes: {len(uncommon_nodes.get('amr2_only', []))}")
    
    node_mapping = {}
    
    # Add common nodes (intersection) - RED
    for g1_node, g2_node in common_nodes:
        union_id = f"common_{g1_node}_{g2_node}"
        g1_attrs = g1.nodes.get(g1_node, {})
        
        union_graph.add_node(union_id, 
                           label=g1_attrs.get('label', g1_node),
                           instance=g1_attrs.get('instance', ''),
                           source='intersection',
                           g1_id=g1_node,
                           g2_id=g2_node)
        
        node_mapping[f"g1_{g1_node}"] = union_id
        node_mapping[f"g2_{g2_node}"] = union_id
    
    # Add AMR1-only nodes - BLUE
    for node in uncommon_nodes.get('amr1_only', []):
        union_id = f"amr1_{node}"
        attrs = g1.nodes.get(node, {})
        
        union_graph.add_node(union_id,
                           label=attrs.get('label', node),
                           instance=attrs.get('instance', ''),
                           source='amr1',
                           g1_id=node,
                           g2_id=None)
        
        node_mapping[f"g1_{node}"] = union_id
    
    # Add AMR2-only nodes - GREEN
    for node in uncommon_nodes.get('amr2_only', []):
        union_id = f"amr2_{node}"
        attrs = g2.nodes.get(node, {})
        
        union_graph.add_node(union_id,
                           label=attrs.get('label', node),
                           instance=attrs.get('instance', ''),
                           source='amr2',
                           g1_id=None,
                           g2_id=node)
        
        node_mapping[f"g2_{node}"] = union_id
    
    # Add edges with proper source tracking
    edge_tracker = {}
    
    # Add edges from G1
    for src, tgt, attrs in g1.edges(data=True):
        src_union = node_mapping.get(f"g1_{src}")
        tgt_union = node_mapping.get(f"g1_{tgt}")
        
        if src_union and tgt_union:
            edge_key = (src_union, tgt_union, attrs.get('role', ''))
            if edge_key not in edge_tracker:
                union_graph.add_edge(src_union, tgt_union, 
                                   role=attrs.get('role', ''),
                                   label=attrs.get('label', ''),
                                   sources=['g1'],
                                   overlap=False)
                edge_tracker[edge_key] = ['g1']
    
    # Add edges from G2
    for src, tgt, attrs in g2.edges(data=True):
        src_union = node_mapping.get(f"g2_{src}")
        tgt_union = node_mapping.get(f"g2_{tgt}")
        
        if src_union and tgt_union:
            edge_key = (src_union, tgt_union, attrs.get('role', ''))
            if edge_key in edge_tracker:
                # This edge exists in both graphs - mark as intersection
                union_graph.edges[src_union, tgt_union]['overlap'] = True
                union_graph.edges[src_union, tgt_union]['sources'] = ['g1', 'g2']
            else:
                union_graph.add_edge(src_union, tgt_union,
                                   role=attrs.get('role', ''),
                                   label=attrs.get('label', ''),
                                   sources=['g2'],
                                   overlap=False)
    
    return union_graph

def render_improved_union_graph(union_graph, output_path):
    """Render improved union graph with hierarchical layout"""
    
    # Count nodes by source
    intersection_nodes = [n for n, attrs in union_graph.nodes(data=True) if attrs.get('source') == 'intersection']
    amr1_nodes = [n for n, attrs in union_graph.nodes(data=True) if attrs.get('source') == 'amr1']
    amr2_nodes = [n for n, attrs in union_graph.nodes(data=True) if attrs.get('source') == 'amr2']
    
    # Count edges by overlap
    intersection_edges = [(s, t) for s, t, attrs in union_graph.edges(data=True) if attrs.get('overlap', False)]
    
    width, height = 1200, 800
    
    # Get hierarchical positions
    positions = calculate_hierarchical_positions(union_graph, width, height)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background: white; border: 1px solid #ddd;">
  <title>AMR Union Graph - Improved</title>
  
  <!-- Title and Statistics -->
  <text x="{width//2}" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold">
    AMR Union Graph - Intersection Highlighted
  </text>
  
  <text x="20" y="60" font-family="Arial" font-size="12" fill="#666">
    Intersection: {len(intersection_nodes)} | AMR1 only: {len(amr1_nodes)} | AMR2 only: {len(amr2_nodes)} nodes | Common edges: {len(intersection_edges)}
  </text>
  
  <!-- Arrow markers -->
  <defs>
    <marker id="arrow-red" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="#E74C3C"/>
    </marker>
    <marker id="arrow-blue" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="#3498DB"/>
    </marker>
    <marker id="arrow-green" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0, 10 4, 0 8" fill="#27AE60"/>
    </marker>
  </defs>
  
  <!-- Edges -->
'''
    
    # Draw edges
    for src, tgt, attrs in union_graph.edges(data=True):
        if src not in positions or tgt not in positions:
            continue
            
        src_pos = positions[src]
        tgt_pos = positions[tgt]
        
        if attrs.get('overlap', False):
            color = '#E74C3C'  # Red for intersection
            marker = 'arrow-red'
            stroke_width = 3
        elif 'g1' in attrs.get('sources', []):
            color = '#3498DB'  # Blue for AMR1
            marker = 'arrow-blue'
            stroke_width = 2
        else:
            color = '#27AE60'  # Green for AMR2
            marker = 'arrow-green'
            stroke_width = 2
        
        role = attrs.get('role', '').replace(':', '')
        
        svg_content += f'''
  <line x1="{src_pos['x']}" y1="{src_pos['y']}" x2="{tgt_pos['x']}" y2="{tgt_pos['y']}" 
        stroke="{color}" stroke-width="{stroke_width}" marker-end="url(#{marker})" opacity="0.8"/>
  <text x="{(src_pos['x'] + tgt_pos['x'])/2}" y="{(src_pos['y'] + tgt_pos['y'])/2 - 5}" 
        font-family="Arial" font-size="9" fill="{color}" font-weight="bold" text-anchor="middle">{role}</text>
'''
    
    svg_content += '\n  <!-- Nodes -->\n'
    
    # Draw nodes
    for node, attrs in union_graph.nodes(data=True):
        if node not in positions:
            continue
            
        pos = positions[node]
        
        if attrs.get('source') == 'intersection':
            fill_color = '#FF6B6B'  # Light red
            stroke_color = '#E74C3C'  # Dark red
            stroke_width = 3
        elif attrs.get('source') == 'amr1':
            fill_color = '#74C0FC'  # Light blue
            stroke_color = '#3498DB'  # Dark blue
            stroke_width = 2
        else:
            fill_color = '#8CE99A'  # Light green
            stroke_color = '#27AE60'  # Dark green
            stroke_width = 2
        
        label = attrs.get('label', attrs.get('instance', node.split('_')[-1]))
        if len(label) > 12:
            label = label[:10] + '..'
        
        # Determine node type
        is_literal = (label.startswith('"') or '_op' in node or 
                     any(x in label.lower() for x in ['"', 'associated', 'press', 'arkansas', 'australia', 'ipod', 'fbi', 'syed', 'farook']))
        
        if is_literal:
            rect_width = max(60, len(label) * 8)
            rect_height = 25
            
            svg_content += f'''
  <rect x="{pos['x'] - rect_width//2}" y="{pos['y'] - rect_height//2}" 
        width="{rect_width}" height="{rect_height}" fill="{fill_color}" 
        stroke="{stroke_color}" stroke-width="{stroke_width}" rx="8"/>
'''
        else:
            radius = 25
            
            svg_content += f'''
  <circle cx="{pos['x']}" cy="{pos['y']}" r="{radius}" 
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>
'''
        
        svg_content += f'''
  <text x="{pos['x']}" y="{pos['y'] + 4}" text-anchor="middle" 
        font-family="Arial" font-size="11" font-weight="bold" fill="white">{label}</text>
'''
    
    svg_content += '''
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ Union graph saved: {output_path}")
    print(f"   Intersection: {len(intersection_nodes)} nodes, {len(intersection_edges)} edges")
    print(f"   AMR1-only: {len(amr1_nodes)} nodes")
    print(f"   AMR2-only: {len(amr2_nodes)} nodes")

def main():
    parser = argparse.ArgumentParser(description="Complete AMR Visualizer - Individual + Union")
    parser.add_argument("--amr1", required=True, help="Path to first AMR file")
    parser.add_argument("--amr2", required=True, help="Path to second AMR file")
    parser.add_argument("--alignment", required=True, help="Path to alignment.json")
    parser.add_argument("--out1", default="amr1_individual.svg", help="Output SVG for AMR1")
    parser.add_argument("--out2", default="amr2_individual.svg", help="Output SVG for AMR2")
    parser.add_argument("--union", default="union_graph.svg", help="Output SVG for union graph")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    try:
        print("🚀 Complete AMR Visualization Pipeline")
        print("="*50)
        
        # Load AMR graphs
        with open(args.amr1, 'r', encoding='utf-8') as f:
            amr1_content = f.read()
        
        with open(args.amr2, 'r', encoding='utf-8') as f:
            amr2_content = f.read()
        
        print("📖 Loading AMR graphs...")
        g1 = load_amr_graph(amr1_content)
        g2 = load_amr_graph(amr2_content)
        
        print(f"   AMR1: {len(g1.nodes())} nodes, {len(g1.edges())} edges")
        print(f"   AMR2: {len(g2.nodes())} nodes, {len(g2.edges())} edges")
        
        # Load alignment and annotate graphs
        with open(args.alignment, 'r', encoding='utf-8') as f:
            alignment_data = json.load(f)
        
        print("🔗 Annotating overlap information...")
        annotate_overlap(g1, g2, args.alignment)
        
        # Generate individual graphs
        print("🎨 Rendering individual graphs...")
        render_individual_graph(g1, args.out1, "AMR Graph 1")
        render_individual_graph(g2, args.out2, "AMR Graph 2")
        
        # Generate union graph
        print("🔄 Creating union graph...")
        union_graph = create_improved_union_graph(g1, g2, alignment_data)
        render_improved_union_graph(union_graph, args.union)
        
        print("\n✨ Visualization complete!")
        print(f"📊 Individual graphs: {args.out1}, {args.out2}")
        print(f"🔗 Union graph: {args.union}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())