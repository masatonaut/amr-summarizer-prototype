import amrlib

def parse_amr(text: str) -> str:
    """
    Parse the input text into an AMR graph using amrlib's public API.
    
    Parameters:
        text (str): The input sentence or text to parse.
        
    Returns:
        str: The AMR graph representation as a string.
    """
    # Load the default stog model. Note: This may take some time on the first call.
    stog = amrlib.load_stog_model()
    graphs = stog.parse_sents([text])
    return graphs[0]
