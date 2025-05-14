"""
Each index term is associated with an inverted list
- Contains lists of documents, or lists of word occurrences in documents, and other information
- Each entry is called a posting
- The part of the posting that refers to a specific document or location is called a pointer
- Each document in the collection is given a unique number
- Lists are usually document-ordered (sorted by document number)
"""

from collections import defaultdict
from utils.posting import Posting


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to a list of postings 
    """

    def __init__(self, fp='./index.shelve') -> None:
        self._fp = fp

        self._BATCH_SIZE = 5
        self._current_batch = defaultdict(list)

    def _sync_batch(self) -> None:
        raise NotImplementedError()
        self._current_batch.clear()

    def add_posting(self, term: str, posting: Posting) -> None:
        """Add a posting to the inverted index."""
        insert_index = 0
        # determine the correct location to insert
        while insert_index < len(self._current_batch[term]) and self._current_batch[term][insert_index].doc_id < posting.doc_id:
            insert_index += 1
        self._current_batch[term].insert(insert_index, posting)
