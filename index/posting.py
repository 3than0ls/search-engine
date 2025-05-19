from dataclasses import dataclass
import struct


POSTING_FORMAT = "<II"
POSTING_SIZE = struct.calcsize(POSTING_FORMAT)


@dataclass(order=True)
class Posting:
    """A singular posting for a posting list in an inverted index. Posting is dumb and doesn't actually know what term it's for."""
    doc_id: int
    term_frequency: int
    # tfidf_score: float = 1
    # url: str = ""

    def __str__(self) -> str:
        return f"<Posting | {self.doc_id}, {self.term_frequency}>"

    def __repr__(self) -> str:
        return self.__str__()

    def serialize(self) -> bytes:
        """
        Return a serialized representation for disk storage. If you want to add more fields, you'll need to update the _STRUCT_FORMAT variable, then add it as an argument to .pack()
        https://docs.python.org/3/library/struct.html#struct.pack
        https://docs.python.org/3/library/struct.html#format-characters
        """
        return struct.pack(POSTING_FORMAT, self.doc_id, self.term_frequency)

    @staticmethod
    def deserialize(b: bytes) -> "Posting":
        """Return a Posting object from a struct serialized representation."""
        doc_id, term_frequency = struct.unpack(POSTING_FORMAT, b)
        return Posting(doc_id=doc_id, term_frequency=term_frequency)
