from collections import Counter, defaultdict
from bs4 import BeautifulSoup
from typing import Mapping
from index.posting_list import PostingList
from index.term import Term
from index.posting import Posting
import nltk
from nltk.stem import PorterStemmer


def tokenize(text: str) -> Counter[str]:
    """
    Tokenizes input text, applies Porter stemming, and returns a Counter object.
    """
    stemmer = PorterStemmer()
    tokens = Counter()

    buffer = ""
    cursor = 0

    while cursor < len(text):
        char = text[cursor]
        if char.isalnum():
            buffer += char.lower()
        else:
            if buffer:
                # stem token
                stemmed_token = stemmer.stem(buffer)
                tokens[stemmed_token] += 1
                buffer = ""
        cursor += 1

    # append anything leftover in the buffer after stemming
    if buffer:
        stemmed_token = stemmer.stem(buffer)
        tokens[stemmed_token] += 1

    return tokens


_TAG_WEIGHTS = {
    'title': 5,
    'h1': 4,
    'h2': 3,
    'h3': 2,
    'b': 2,
    'strong': 2,
    'p': 1,
    'body': 1,
    'span': 1,
    'div': 1,
}

_TAGS = list(_TAG_WEIGHTS.keys())


def get_postings(doc_id: int, soup: BeautifulSoup) -> Mapping[Term, PostingList]:
    """
    Returns a Mapping of Terms to PostingLists.
    Only takes text from the tags in _TAG_WEIGHTS keys, ignoring all other data.
    """
    token_tf_map: defaultdict[str, int] = defaultdict(int)

    # weight specific terms based on HTML tags
    for tag in soup.find_all(_TAGS):
        tokens = tokenize(tag.get_text(separator=" ", strip=True))
        for token, count in tokens.items():
            token_tf_map[token] += count * _TAG_WEIGHTS[tag.name]

    out: defaultdict[Term, PostingList] = defaultdict(PostingList)
    for token, tf in token_tf_map.items():
        out[Term(token)].add_posting(Posting(doc_id, tf))

    return out


def get_anchor_word_postings(doc_id_map: Mapping[int, str], soup: BeautifulSoup) -> Mapping[Term, PostingList]:
    """
    Extracts anchor texts from one soup and creates postings for them for the document they link to.
    """
    out: defaultdict[Term, PostingList] = defaultdict(PostingList)
    inverted = {v: k for k, v in doc_id_map.items()}

    a_tags = []
    # a_tags.extend(soup.find_all('a', href=True))
    for a_tag in a_tags:
        if a_tag is None:
            continue
        href = a_tag['href'].split('#')[0]  # ignore fragment part
        if not href.startswith('http'):
            continue
        doc_id = inverted.get(href, None)
        if doc_id is None:
            continue
        tokens = tokenize(a_tag.get_text(separator=" ", strip=True))
        for token, count in tokens.items():
            out[Term(token)].add_posting(Posting(doc_id, count))

    return out
