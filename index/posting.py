from dataclasses import dataclass
import sys

from index.delimeters import POSTING_DELIMETER


@dataclass(order=True)
class Posting:
    """A singular posting for a posting list in an inverted index. Posting is dumb and doesn't actually know what term it's for."""
    doc_id: str  # hash
    term_frequency: int
    # tfidf_score: float = 1
    # url: str = ""

    def __str__(self):
        return f"<Posting with doc ID {self.doc_id}>"

    def serialize(self):
        """Return a serialized representation for disk storage."""
        return POSTING_DELIMETER.join([self.doc_id, str(self.term_frequency)])


if __name__ == '__main__':
    import pickle
    index_sample = {
        f"term_______{i}": [Posting(f"doc_id_{i**2}", i**4), Posting(f"doc_id_{i**2}", i**5)] for i in range(25)
    }
    test_string = ""
    test_pickle_string_mix = ""
    for term, postings in index_sample.items():
        test_string += f"{term}\n"
        test_pickle_string_mix += f"{term}\n"
        for posting in postings:
            test_string += f"{posting.doc_id}|{posting.term_frequency}"
            print(str(pickle.dumps(posting)))
            test_pickle_string_mix += str(pickle.dumps(posting))
        test_string += "\n"
    # print(test_string)

    print("dictionary size")
    print(sys.getsizeof(index_sample))
    print("test_pickle_string_mix size")
    exit()
    print(sys.getsizeof(test_pickle_string_mix))
    print("string size")
    print(sys.getsizeof(test_string))
    print("encoded string size")
    print(sys.getsizeof(test_string.encode()))
    print("pickle size")
    print(sys.getsizeof(pickle.dumps(index_sample)))
