from index.posting import Posting, POSTING_SIZE
from typing import Iterator
import struct


POSTING_LIST_LENGTH_FORMAT = "<H"
POSTING_LIST_LENGTH_SIZE = struct.calcsize(POSTING_LIST_LENGTH_FORMAT)


class PostingList:
    """A list of postings for a single term. PostingList should be dumb and doesn't know what term it's for, nor if it's ordered correctly."""

    def __init__(self) -> None:
        self._postings: list[Posting] = []

    def __len__(self) -> int:
        return len(self._postings)

    def __eq__(self, other) -> bool:
        return isinstance(other, PostingList) and self._postings == other._postings

    def __iter__(self) -> Iterator[Posting]:
        yield from self._postings

    def add_posting(self, posting: Posting) -> None:
        """       
        `add_posting` iterates through the posting list for the term until it finds the correct location to insert the posting.
        This could be optimized using a binary tree, but would make merging much more complicated. 
        This merging issue could be solved by using external libraries.
        """
        insert_index = len(self._postings)
        # determine the correct location to insert
        while insert_index > 0 and self._postings[insert_index - 1].doc_id >= posting.doc_id:
            assert self._postings[insert_index - 1].doc_id != posting.doc_id, \
                f"Found duplicate posting document ID. {posting}"
            insert_index -= 1

        self._postings.insert(insert_index, posting)

    def serialize(self) -> bytes:
        """
        Return a serialized representation for disk storage in binary.
        First portion is number of postings (in bytes), second portion is the serialization of the postings
        """
        serialized_postings = b''.join(
            [posting.serialize() for posting in self._postings])
        return struct.pack(POSTING_LIST_LENGTH_FORMAT, len(self._postings)) + serialized_postings
        return b''.join([posting.serialize() for posting in self._postings])

    @staticmethod
    def deserialize(data: bytes) -> "PostingList":
        """Return a PostingList object from a struct serialized representation. Postings are deserialized because we know their exact size. Assumes data attribute is contains only the posting list."""
        # I hate this so much i hate hate hate byte serialization
        out = PostingList()

        posting_list_length = struct.unpack(
            POSTING_LIST_LENGTH_FORMAT, data[:POSTING_LIST_LENGTH_SIZE])[0]
        posting_list_data = data[POSTING_LIST_LENGTH_SIZE:
                                 POSTING_LIST_LENGTH_SIZE + posting_list_length * POSTING_SIZE]

        for i in range(0, len(posting_list_data), POSTING_SIZE):
            posting = Posting.deserialize(
                posting_list_data[i:i + POSTING_SIZE])
            out._postings.append(posting)
        return out
