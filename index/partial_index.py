from collections import defaultdict
from index.posting import Posting
from index.posting_list import PostingList
from index.delimeters import INVERTED_INDEX_KV_DELIMETER, INVERTED_INDEX_DELIMETER
from utils.logger import index_log
import os
from pathlib import Path


class PartialIndex:
    """
    PartialIndex-es are only used in the construction of the InvertedIndex class.
    The Indexer class creates numerous PartialIndex-es and merges them into one InvertedIndex.
    PartialIndex-es are a container mapping terms (strings) to a list of postings (PostingList).
    """

    def __init__(self, partial_index_id: int, partial_index_dir: Path) -> None:
        self._partial_index_dir = partial_index_dir

        self._index = defaultdict(PostingList)
        self._id = partial_index_id
        self._fp = Path(
            f"{self._partial_index_dir}/partial_index_{self._id:03}.txt")

        # track the total number of postings added, used for determining when to dump partial index to disk
        self._num_postings = 0

    def num_terms(self) -> int:
        return len(self._index)

    def num_postings(self) -> int:
        return self._num_postings

    def dump(self) -> None:
        """Dumps the current partial index to disk."""
        # I should probably have a variable ensuring that the partial index is only dumped once, but I trust myself to not be stupid
        self._partial_index_dir.mkdir(exist_ok=True)
        fname = f"partial_index_{self._id:03}.txt"
        path = self._partial_index_dir / fname

        index_log.info(
            f"Dumping partial index ID {self._id} to {path}")

        # may want to do wb and .encode('utf-8') for performance benefits (smaller disk size)
        with open(path, 'w', encoding='utf-8') as f:
            for term, postings in self._index.items():
                line = f"{term}{INVERTED_INDEX_KV_DELIMETER}{postings.serialize()}"
                f.write(line)
                f.write(INVERTED_INDEX_DELIMETER)

    def add_posting(self, term: str, posting: Posting) -> None:
        """
        Add a posting to the inverted index. Postings are ordered by document ID.
        """
        self._index[term].add_posting(posting)

        self._num_postings += 1

    def __str__(self):
        return f"<PartialIndex ID {self._id} | {self.num_terms()} terms, {self._num_postings} postings>"
