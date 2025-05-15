from dataclasses import dataclass
import sys


@dataclass(order=True)
class Posting:
    doc_id: str  # hash
    term_frequency: int
    tfidf_score: float = 1
    url: str = ""


POSTING_SIZE = sys.getsizeof(Posting('', 0))


if __name__ == '__main__':
    import functools
    inst_size = sys.getsizeof(Posting('test', 0)) / 1024
    NUM_INSTANCES = 10000
    instances = [Posting(str(i), i) for i in range(NUM_INSTANCES)]
    instances_size = functools.reduce(
        lambda acc, obj: acc + sys.getsizeof(obj),
        instances,
        0
    ) / 1024
    print(
        f"Instance size: {inst_size}KB\n{NUM_INSTANCES} Instances: {instances_size}KB")

    batch_size = (2 ** 28) / POSTING_SIZE
    print(f"Batch size: {2 ** 28} / {POSTING_SIZE}")
    print(f"Batch size: {batch_size}")

    import pickle
    index_sample = {
        f"term_______{i}": [Posting(f"doc_id_{i**2}", i**4), Posting(f"doc_id_{i**2}", i**5)] for i in range(25)
    }
    test_string = ""
    for term, postings in index_sample.items():
        test_string += f"{term}\n"
        for posting in postings:
            test_string += f"{posting.doc_id}|{posting.term_frequency}|{posting.tfidf_score}|{posting.url};"
        test_string += "\n"
    # print(test_string)

    print("dictionary size")
    print(sys.getsizeof(index_sample))
    print("string size")
    print(sys.getsizeof(test_string))
    print("encoded string size")
    print(sys.getsizeof(test_string.encode()))
    print("pickle size")
    print(sys.getsizeof(pickle.dumps(index_sample)))
