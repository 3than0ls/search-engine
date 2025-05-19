from collections import Counter


def _tokenize(text: str) -> Counter[str]:
    """
    ADAPTED FROM ASSIGNMENT 1
    Returns a Counter object representing the count of all tokens.
    Typically this text is extracted from a BeautifulSoup via get_text().
    """
    tokens = Counter()

    buffer = ""
    cursor = 0

    while cursor < len(text):
        char = text[cursor]
        if char.isalnum():
            buffer += char.lower()
        else:
            if buffer:
                tokens[buffer] += 1
                buffer = ""
        cursor += 1

    # append anything leftover in the buffer
    if buffer:
        tokens[buffer] += 1

    return tokens


def get_tokens(text: str) -> Counter[str]:
    """
    Returns a Counter object representing the count of all tokens.
    Typically this text is extracted from a BeautifulSoup via get_text().
    """
    tokens = _tokenize(text)
    words = Counter({
        token: count for token, count in tokens.items()
    })
    return words
