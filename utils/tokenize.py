from collections import Counter, defaultdict
from bs4 import BeautifulSoup
from typing import Mapping
from index.posting_list import PostingList
from index.term import Term
from index.posting import Posting


def _tokenize(text: str) -> Counter[str]:
    """
    ADAPTED FROM ASSIGNMENT 1
    Returns a Counter object representing the count of all tokens.
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


def get_postings(doc_id: int, soup: BeautifulSoup) -> Mapping[Term, PostingList]:
    """
    Returns a Mapping of Terms to PostingLists.
    Must maintain this header for use.
    TODO: Update it to utilize td-idf scores and pointers and whatnot.
    """
    tokens = _tokenize(soup.get_text(separator=" ", strip=True))
    out: defaultdict[Term, PostingList] = defaultdict(PostingList)

    for token, count in tokens.items():
        out[Term(token)].add_posting(Posting(doc_id, count))

    return out
