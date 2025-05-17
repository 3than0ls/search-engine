from index.posting import Posting
from index.delimeters import POSTING_LIST_DELIMETER
from typing import Iterator


class PostingList:
    """A list of postings for a single term. PostingList should be dumb and doesn't know what term it's for."""

    def __init__(self) -> None:
        self._postings: list[Posting] = []

    def __len__(self) -> int:
        return len(self._postings)

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

    def serialize(self) -> str:
        return POSTING_LIST_DELIMETER.join([posting.serialize() for posting in self._postings])
