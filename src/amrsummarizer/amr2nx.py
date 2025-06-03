import networkx as nx
from penman import decode
import re


def clean_amr_content(amr_string: str) -> str:
    """
    Clean AMR content by removing comments and fixing formatting
    """
    import re
    
    content = amr_string.strip()
    
    print(f"DEBUG: Original content length: {len(content)}")
    print(f"DEBUG: First 100 chars: {repr(content[:100])}")
    
    # Remove outer quotes if the entire content is wrapped in quotes
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
        print("DEBUG: Removed outer quotes")
    
    # Look for the AMR structure more intelligently
    # Fallback: find the largest parenthetical structure that contains " / "
    max_content = ""
    start_pos = 0
    
    while True:
        paren_start = content.find('(', start_pos)
        if paren_start == -1:
            break
        
        # Try to find the matching closing parenthesis
        paren_count = 0
        paren_end = paren_start
        
        for i in range(paren_start, len(content)):
            if content[i] == '(':
                paren_count += 1
            elif content[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    paren_end = i
                    break
        
        if paren_count == 0:  # Found complete parenthetical structure
            candidate = content[paren_start:paren_end + 1].strip()
            if len(candidate) > len(max_content) and ' / ' in candidate:
                max_content = candidate
        
        start_pos = paren_start + 1
    
    if max_content:
        amr_content = max_content
        print(f"DEBUG: Found structure of length: {len(amr_content)}")
    else:
        raise ValueError("Could not find AMR structure")
    
    print(f"DEBUG: Extracted AMR length: {len(amr_content)}")
    
    # Fix double quotes in string literals (""word"" -> "word")
    amr_content = re.sub(r'""([^"]*?)""', r'"\1"', amr_content)
    
    # Additional cleanup: remove any trailing quotes that might be left
    amr_content = amr_content.rstrip('"')
    
    print(f"DEBUG: Final AMR content (first 200 chars): {repr(amr_content[:200])}")
    
    return amr_content


def load_amr_graph(amr_string: str) -> nx.DiGraph:
    """
    Load an AMR string and convert it to a NetworkX directed graph.
    
    Args:
        amr_string: AMR in PENMAN notation (possibly with comments)
        
    Returns:
        NetworkX DiGraph representing the AMR
    """
    try:
        # Clean the AMR content
        clean_amr = clean_amr_content(amr_string)
        
        # Parse with penman
        graph = decode(clean_amr)
        
        # Convert to NetworkX
        G = nx.DiGraph()
        
        # Add nodes and edges from the triples
        for triple in graph.triples:
            source, role, target = triple
            
            # Skip None values
            if source is None or role is None or target is None:
                continue
            
            # Add nodes
            G.add_node(source)
            if isinstance(target, str) and not target.startswith('"'):
                G.add_node(target)
            
            # Add edge with role as attribute
            if role == ":instance":
                # For instance relations, add as node attribute
                G.nodes[source]['instance'] = target
                G.nodes[source]['label'] = target
            else:
                # For other relations, add as edge
                if isinstance(target, str) and not target.startswith('"'):
                    # Target is a variable
                    G.add_edge(source, target, role=role, label=role)
                else:
                    # Target is a literal - create a literal node
                    literal_node = f"{source}_{role}_{target}"
                    G.add_node(literal_node, literal=target, label=target)
                    G.add_edge(source, literal_node, role=role, label=role)
        
        return G
        
    except Exception as e:
        print(f"Error loading AMR graph: {e}")
        print(f"AMR content preview: {amr_string[:200]}...")
        raise


def amr_to_networkx(amr_file_path: str) -> nx.DiGraph:
    """
    Load AMR from file and convert to NetworkX graph.
    
    Args:
        amr_file_path: Path to AMR file
        
    Returns:
        NetworkX DiGraph
    """
    with open(amr_file_path, 'r', encoding='utf-8') as f:
        amr_content = f.read()
    
    return load_amr_graph(amr_content)


def display_graph_info(G: nx.DiGraph, name: str = "Graph"):
    """
    Display information about the graph for debugging
    """
    print(f"=== {name} Info ===")
    print(f"Nodes: {len(G.nodes())}")
    print(f"Edges: {len(G.edges())}")
    print(f"Node list: {list(G.nodes())[:10]}...")  # First 10 nodes
    print(f"Edge list: {list(G.edges(data=True))[:5]}...")  # First 5 edges
    print()


if __name__ == "__main__":
    # Test the functions
    test_amr = '''
    # ::snt This is a test sentence.
    (t / test-01
       :ARG0 (i / i)
       :ARG1 (s / sentence))
    '''
    
    try:
        G = load_amr_graph(test_amr)
        display_graph_info(G, "Test AMR")
    except Exception as e:
        print(f"Test failed: {e}")
