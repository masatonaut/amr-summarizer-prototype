import networkx as nx
from penman import decode
import re

def clean_amr_content(amr_string: str) -> str:
    """
    Clean AMR content by removing comments and fixing formatting
    """
    content = amr_string.strip()
    
    print(f"DEBUG: Original content length: {len(content)}")
    print(f"DEBUG: First 100 chars: {repr(content[:100])}")
    
    # Remove outer quotes if the entire content is wrapped in quotes
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
        print("DEBUG: Removed outer quotes")
    
    # Remove comment lines that start with #
    lines = content.split('\n')
    amr_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('#') and stripped:
            amr_lines.append(line)
    
    if amr_lines:
        content = '\n'.join(amr_lines)
        print(f"DEBUG: After removing comments, length: {len(content)}")
    
    # Look for the AMR structure - find the main parenthetical structure
    paren_start = content.find('(')
    if paren_start == -1:
        raise ValueError("Could not find AMR structure (no opening parenthesis)")
    
    # Find the matching closing parenthesis
    paren_count = 0
    paren_end = len(content) - 1
    
    for i in range(paren_start, len(content)):
        if content[i] == '(':
            paren_count += 1
        elif content[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                paren_end = i
                break
    
    if paren_count != 0:
        raise ValueError("Unmatched parentheses in AMR structure")
    
    amr_content = content[paren_start:paren_end + 1].strip()
    print(f"DEBUG: Extracted AMR length: {len(amr_content)}")
    
    # Fix double quotes in string literals (""word"" -> "word")
    amr_content = re.sub(r'""([^"]*?)""', r'"\1"', amr_content)
    
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
        
        print(f"DEBUG: Attempting to parse with penman...")
        print(f"DEBUG: Clean AMR first 300 chars: {clean_amr[:300]}")
        
        # Parse with penman
        graph = decode(clean_amr)
        print(f"DEBUG: Penman parsing successful, {len(graph.triples)} triples")
        
        # Convert to NetworkX
        G = nx.DiGraph()
        
        # Add nodes and edges from the triples
        for triple in graph.triples:
            source, role, target = triple
            
            print(f"DEBUG: Processing triple: {source} {role} {target}")
            
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
                print(f"DEBUG: Added instance {source} -> {target}")
            else:
                # For other relations, add as edge
                if isinstance(target, str) and not target.startswith('"'):
                    # Target is a variable
                    G.add_edge(source, target, role=role, label=role)
                    print(f"DEBUG: Added edge {source} -[{role}]-> {target}")
                else:
                    # Target is a literal - create a literal node
                    literal_node = f"{source}_{role.replace(':', '')}_{str(target).replace('\"', '')}"
                    G.add_node(literal_node, literal=target, label=str(target))
                    G.add_edge(source, literal_node, role=role, label=role)
                    print(f"DEBUG: Added literal edge {source} -[{role}]-> {literal_node}")
        
        print(f"DEBUG: Final graph: {len(G.nodes())} nodes, {len(G.edges())} edges")
        print(f"DEBUG: Nodes: {list(G.nodes())}")
        print(f"DEBUG: Edges: {list(G.edges(data=True))[:5]}...")
        
        return G
        
    except Exception as e:
        print(f"Error loading AMR graph: {e}")
        print(f"AMR content preview: {amr_string[:200]}...")
        import traceback
        traceback.print_exc()
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