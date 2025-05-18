"""
Each index term is associated with an inverted list
- Contains lists of documents, or lists of word occurrences in documents, and other information
- Each entry is called a posting
- The part of the posting that refers to a specific document or location is called a pointer
- Each document in the collection is given a unique number
- Lists are usually document-ordered (sorted by document number)
"""

from collections import defaultdict
from index.posting import Posting
from index.posting_list import PostingList
from utils.logger import index_log
import os
from pathlib import Path


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to postings PostingList (`PostingList`).

    This class is used to provide a simple interface for term lookup and retrieval, hiding away the details of how the index is created and stored.
    There are NO methods for adding or removing postings from the index. InvertedIndex is read-only, and based off of data specified from `index_dir`.
    """

    def __init__(self, index_dir: Path) -> None:
        self._index_dir = index_dir

        # needs initialization
        self._num_terms = 0
        self._num_postings = 0

    def get_postings(self, term: str) -> list[Posting]:
        """Returns a list of postings for a given term. Works by opening the index file, seeking to the correct location, and reading the postings list, return the list of results."""
        raise NotImplementedError

    def __str__(self):
        return f"<InvertedIndex stored at {self._index_dir} | {self._num_terms} terms, {self._num_postings} postings>"
