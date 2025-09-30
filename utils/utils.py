



def chunk_text(text: str, n_char: int, overlap: int = 0):
    """
    Splits a given text into overlapping chunks of specified length.
    Args:
        text (str): The input string to be chunked.
        n_char (int): The length of each chunk.
        overlap (int, optional): The number of characters each chunk should overlap with the previous chunk. Defaults to 0.
    Returns:
        List[str]: A list of string chunks.
    Raises:
        ValueError: If overlap is greater than or equal to n_char.
    Example:
        >>> chunk("abcdefg", 3, 1)
        ['abc', 'cde', 'efg']
    """

    if overlap >= n_char:
        raise ValueError("Overlap must be less than n_char")
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + n_char
        chunks.append(text[start:end])
        start += n_char - overlap
    return chunks



def filter_json(json_str:str) -> str:
    """
    Filters a JSON string to ensure it is valid and properly formatted.
    Args:
        json_str (str): The input JSON string.
    Returns:
        str: A filtered JSON string with unnecessary characters removed.
    """
    # Remove any non-JSON characters
    json_extra_chars = ['```', '```json', 'json']
    for char in json_extra_chars:
        json_str = json_str.replace(char, '')
    
    json_str = json_str.replace('(', '{')
    json_str = json_str.replace(')', '}')

    filtered_json = ''.join(c for c in json_str if c.isprintable() or c.isspace())
    
    
    return filtered_json.strip()
