from dataclasses import dataclass
import struct

TERM_LENGTH_FORMAT = "<H"
TERM_LENGTH_SIZE = struct.calcsize(TERM_LENGTH_FORMAT)


@dataclass(order=True)
class Term:
    term: str

    def __hash__(self) -> int:
        return hash(self.term)

    def __eq__(self, other) -> bool:
        return isinstance(other, Term) and self.term == other.term

    def serialize(self) -> bytes:
        """
        Return a serialized representation for disk storage in binary.
        First portion is length of term (in bytes), second portion is the term
        """
        encoded_term = self.term.encode("utf-8")
        return struct.pack(TERM_LENGTH_FORMAT, len(encoded_term)) + encoded_term

    @staticmethod
    def deserialize(data: bytes) -> "Term":
        """
        Return a Posting object from a struct serialized representation. 
        Assumes data must be of correct content (contain a portion stating term length and term encoded), but all leading data after is ignored.
        """
        term_length = struct.unpack(
            TERM_LENGTH_FORMAT, data[:TERM_LENGTH_SIZE])[0]
        term_data = data[TERM_LENGTH_SIZE:TERM_LENGTH_SIZE + term_length]
        return Term(term_data.decode("utf-8"))
