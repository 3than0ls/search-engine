from collections import defaultdict
from typing import DefaultDict, Iterator, Tuple, Optional
from index.posting import Posting
from index.posting_list import PostingList, POSTING_LIST_LENGTH_SIZE, POSTING_LIST_LENGTH_FORMAT
from index.term import Term, TERM_LENGTH_SIZE, TERM_LENGTH_FORMAT
from index.posting import POSTING_SIZE, POSTING_FORMAT
from utils.logger import index_log
import bisect
from pathlib import Path
import struct


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

        for term, postings_list in PartialIndex.deserialize_single_line(data):
            num_postings += len(postings_list)
            partial_index._index[term] = postings_list
            bisect.insort(partial_index._sorted_terms, term)

        partial_index._num_postings = num_postings
        return partial_index

    @staticmethod
    def deserialize_single_line(data: bytes) -> Iterator[Tuple[Term, PostingList]]:
        cursor = 0
        while cursor < len(data):
            term = Term.deserialize(data[cursor:])
            cursor += TERM_LENGTH_SIZE + len(term.term.encode("utf-8"))
            postings_list = PostingList.deserialize(data[cursor:])
            cursor += POSTING_LIST_LENGTH_SIZE + \
                len(postings_list) * POSTING_SIZE

            yield (term, postings_list)

    def __eq__(self, other):
        return isinstance(other, PartialIndex) and self._sorted_terms == other._sorted_terms and self._index == other._index and self._num_postings == other._num_postings

    def __str__(self):
        return f"<PartialIndex | {self.num_terms()} terms, {self._num_postings} postings>"

    def __repr__(self):
        return self.__str__()


class PartialIndexResource:
    def __init__(self, partial_index_fp: Path) -> None:
        self._partial_index_fp = partial_index_fp
        self._resource = None

    def __enter__(self) -> "PartialIndexResource":
        self._resource = open(self._partial_index_fp, 'rb')
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._resource is not None:
            self._resource.close()

    def __iter__(self) -> Iterator[Tuple[Term, PostingList]]:
        return self.read_items()

    def read_item(self) -> Optional[Tuple[Term, PostingList]]:
        """
        Read a single item and it's posting list from the partial index. Assumes the posting list is in absolute correct format. Must be accessed within a context manager.
        """
        assert self._resource, "PartialIndexResource not opened"
        # probe, if successful, represents the term length raw data
        probe = self._resource.read(TERM_LENGTH_SIZE)
        if probe == b'':
            return None
        term_length = struct.unpack(TERM_LENGTH_FORMAT, probe)[0]
        term = Term.deserialize(probe + self._resource.read(term_length))
        posting_list_length_raw = self._resource.read(POSTING_LIST_LENGTH_SIZE)
        posting_list_length = struct.unpack(
            POSTING_LIST_LENGTH_FORMAT, posting_list_length_raw)[0]
        postings_list = PostingList.deserialize(
            posting_list_length_raw + self._resource.read(posting_list_length * POSTING_SIZE))
        return (term, postings_list)

    def read_items(self) -> Iterator[Tuple[Term, PostingList]]:
        """
        Return a generator of items (term, postings) from the partial index.
        Probably not used at all.
        """
        while item := self.read_item():
            yield item
