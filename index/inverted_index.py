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
from index.delimeters import INVERTED_INDEX_KV_DELIMETER, INVERTED_INDEX_DELIMETER
from utils.logger import index_log
import os
from pathlib import Path


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to postings PostingList (`PostingList`).

    There was an idea (and implementation!) that updated a serialized inverted index in batches, and I believe this to be faster for this project
    However, specifications require that you dump out partial indexes which are then merged at the end.
    To be fair, the real world does use this.
    """

    def __init__(self, partial_index_dir=os.environ.get("PARTIAL_INDEX_DIR")) -> None:
        if not partial_index_dir:
            raise ValueError(f"Partial index directory must be set.")

        self._partial_index_dir = Path(partial_index_dir)

        if not os.environ.get("TESTING") == "true" and \
                self._partial_index_dir.exists() and any(self._partial_index_dir.iterdir()):
            raise ValueError(
                f"Partial index directory {self._partial_index_dir} is not empty.")

        # batches are also known as partial indexes, but will keep them called batches
        # every 10000 postings, dump the current partial index
        self._BATCH_SIZE = 2 ** 16
        self._partial_index = defaultdict(PostingList)
        self._partial_index_id = 0

        # because we reset the partial index every so often, we must keep track of total numbers ourselves
        self._num_postings = 0
        self._num_terms = 0

        self._add_counter = 0

    def _current_partial_index_name(self) -> str:
        return f"partial_index_{self._partial_index_id}.txt"

    def __enter__(self):
        self._add_counter = self._num_postings
        return self

    def __exit__(self, *args):
        if not os.environ.get("TESTING") == "true" and self._add_counter != self._num_postings:
            self._dump_partial_index()

    def num_terms(self) -> int:
        return self._num_terms

    def num_postings(self) -> int:
        return self._num_postings

    def _dump_partial_index(self) -> None:
        """Dumps the current partial index to disk."""
        self._partial_index_dir.mkdir(exist_ok=True)
        fname = f"partial_index_{self._partial_index_id:03}.txt"
        path = self._partial_index_dir / fname

        index_log.info(f"Dumping current partial index to {path}")

        # may want to do wb and .encode('utf-8') for performance benefits (smaller disk size)
        with open(path, 'w', encoding='utf-8') as f:
            for term, postings in self._partial_index.items():
                line = f"{term}{INVERTED_INDEX_KV_DELIMETER}{postings.serialize()}"
                f.write(line)
                f.write(INVERTED_INDEX_DELIMETER)

        self._partial_index.clear()
        self._partial_index_id += 1

    def add_posting(self, term: str, posting: Posting) -> None:
        """
        Add a posting to the inverted index. Postings are ordered by document ID.
        """
        if len(self._partial_index[term]) == 0:
            self._num_terms += 1

        self._partial_index[term].add_posting(posting)

        self._num_postings += 1

        if self._num_postings % self._BATCH_SIZE == 0:
            self._dump_partial_index()

    def __str__(self):
        return f"<Inverted Index stored in parts at {self._partial_index_dir} | {self._num_terms} terms, {self._num_postings} postings>"
