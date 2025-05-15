"""
Each index term is associated with an inverted list
- Contains lists of documents, or lists of word occurrences in documents, and other information
- Each entry is called a posting
- The part of the posting that refers to a specific document or location is called a pointer
- Each document in the collection is given a unique number
- Lists are usually document-ordered (sorted by document number)
"""

from collections import defaultdict
from index.posting import Posting, POSTING_SIZE
from utils.merge import merge
from utils.logger import index_log
import shelve


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to a list of postings (`Posting`)
    """

    def __init__(self, fp='./index.shelve') -> None:
        self._fp = fp

        # batch size is 32MB divided by the size of a Posting
        # So roughly every 32MBs worth of postings will be synced per batch
        self._BATCH_SIZE = (2 ** 28) / POSTING_SIZE
        self._current_batch = defaultdict(list)
        self._batch_num_postings = 0

        self._num_postings = 0
        self._num_terms = 0

    def num_terms(self) -> int:
        return self._num_terms

    def num_postings(self) -> int:
        return self._num_postings

    def sync(self) -> None:
        """Syncs the batch to disk and clears the current batch."""
        index_log.info(
            f"Syncing batch of {self._batch_num_postings} postings to disk...")

        with shelve.open(self._fp) as index:
            for term, postings in self._current_batch.items():
                shelved_postings = index.get(term, [])
                # merge postings and current_postings
                index[term] = merge(shelved_postings, postings)

        self._batch_num_postings = 0
        self._current_batch.clear()

    def add_posting(self, term: str, posting: Posting) -> None:
        """
        Add a posting to the inverted index. Postings are ordered by document ID

        `add_posting` iterates through the posting list for the term until it finds the correct location to insert the posting.
        This could be optimized using a binary tree, but would make merging much more complicated. 
        This merging issue could be solved by using external libraries.

        Due to the natural alphabetical ordering of the documents when we loop through them, 
        and the fact that the document names are unique IDs themselves, we start at the end to optimize
        to a O(1) average case time.
        This is a operates completely on the assumption that documents are processed by ID in alphabetical ascending order.
        """
        insert_index = len(self._current_batch[term])
        # determine the correct location to insert
        while insert_index > 0 and self._current_batch[term][insert_index - 1].doc_id >= posting.doc_id:
            assert self._current_batch[term][insert_index - 1].doc_id != posting.doc_id, \
                f"Found duplicate posting term: {term}: {posting}"
            insert_index -= 1

        if len(self._current_batch[term]) == 0:
            self._num_terms += 1
        self._num_postings += 1

        self._current_batch[term].insert(insert_index, posting)

        self._batch_num_postings += 1
        # we don't want to do >= self._BATCH_SIZE, because the syncing is asynchronous,
        # and thus after batch sizes has been exceeded, it'll spam more sync() calls
        if self._batch_num_postings % self._BATCH_SIZE == 0:
            self.sync()

    def __str__(self):
        return f"<Inverted Index stored at {self._fp} | {self._num_terms} terms, {self._num_postings} postings>"
