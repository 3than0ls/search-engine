from dataclasses import dataclass
import sys


@dataclass(order=True)
class Posting:
    doc_id: str  # hash
    term_frequency: int
    # tfidf_score: float
    # url: str = ""


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
