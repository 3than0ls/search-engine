from collections import defaultdict
from typing import DefaultDict
from index.posting import Posting
from index.posting_list import PostingList, POSTING_LIST_LENGTH_SIZE
from index.term import Term, TERM_LENGTH_SIZE
from index.posting import POSTING_SIZE
from utils.logger import index_log
import bisect
from pathlib import Path


class PartialIndex:
    """
    PartialIndex-es are only used in the construction of the InvertedIndex class.
    The Indexer class creates numerous PartialIndex-es and merges them into one InvertedIndex.
    PartialIndex-es are a container mapping terms (strings) to a list of postings (PostingList).
    """

    def __init__(self) -> None:
        self._index: DefaultDict[Term, PostingList] = defaultdict(PostingList)
        self._sorted_terms: list[Term] = []

        # track the total number of postings added, used for determining when to dump partial index to disk
        self._num_postings = 0

    def num_terms(self) -> int:
        return len(self._index)

    def num_postings(self) -> int:
        return self._num_postings

    def add_posting(self, term: Term, posting: Posting) -> None:
        """
        Add a posting to the inverted index. Postings are ordered by document ID.
        """
        if term not in self._index:
            bisect.insort(self._sorted_terms, term)
        self._index[term].add_posting(posting)
        self._num_postings += 1

    def serialize(self) -> bytes:
        """
        Don't bother touching it.
        Serialize the partial index as such:

        [TERM SERIALIZATION][POSTING LIST SERIALIZATION]

        ...
        """
        out = b''
        for term in self._sorted_terms:
            postings_list = self._index[term]
            line = term.serialize() + postings_list.serialize()
            out += line
        return out
        # return b''.join([posting.serialize() for posting in self._index.values()])

    @staticmethod
    def deserialize(data: bytes) -> "PartialIndex":
        """NOT MEANT TO BE CALLED, ONLY FOR TESTING PURPOSES ONLY. Partial indexes should be deserialized "line by line" rather than all at once."""
        partial_index = PartialIndex()
        num_postings = 0

        cursor = 0
        # print(len(data))
        while cursor < len(data):
            # print(cursor)
            term = Term.deserialize(data[cursor:])
            # print("bytes for term length:", TERM_LENGTH_SIZE)
            # print("bytes for term:", len(term.term.encode("utf-8")), term.term)
            cursor += TERM_LENGTH_SIZE + len(term.term.encode("utf-8"))
            # print(cursor)
            postings_list = PostingList.deserialize(data[cursor:])
            num_postings += len(postings_list)
            # print("bytes for posting list length:", POSTING_LIST_LENGTH_SIZE)
            # print("bytes for posting list:", POSTING_LIST_LENGTH_SIZE + len(postings_list) * POSTING_SIZE, postings_list._postings)
            cursor += POSTING_LIST_LENGTH_SIZE + \
                len(postings_list) * POSTING_SIZE

            partial_index._index[term] = postings_list
            bisect.insort(partial_index._sorted_terms, term)
        partial_index._num_postings = num_postings
        return partial_index

    def __eq__(self, other):
        return isinstance(other, PartialIndex) and self._sorted_terms == other._sorted_terms and self._index == other._index and self._num_postings == other._num_postings

    def __str__(self):
        return f"<PartialIndex | {self.num_terms()} terms, {self._num_postings} postings>"
