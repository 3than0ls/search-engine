from index.posting_list import PostingList
from index.term import Term
import struct


class PostingLine:
    def __init__(self, term: Term, posting_list: PostingList) -> None:
        self._term = term
        self._posting_list = posting_list

    def serialize(self) -> bytes:
        """
        Return a serialized representation for disk storage in binary.
        This would represent "one line" of the inverted index in the merging step.
        """
        term_serialization = self._term.serialize()

        posting_list_length = len(self._posting_list)
        posting_list_length_serialization = struct.pack(
            "<H", posting_list_length)

        posting_list_serialization = self._posting_list.serialize()

        return term_serialization + posting_list_length_serialization + posting_list_serialization
