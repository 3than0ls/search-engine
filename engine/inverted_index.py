"""
Each index term is associated with an inverted list
- Contains lists of documents, or lists of word occurrences in documents, and other information
- Each entry is called a posting
- The part of the posting that refers to a specific document or location is called a pointer
- Each document in the collection is given a unique number
- Lists are usually document-ordered (sorted by document number)
"""

from pathlib import Path
from index.partial_index.partial_index import PartialIndex
from index import Term, PostingList
from utils.tokenize import tokenize
import json


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to postings PostingList (`PostingList`).

    This class is used to provide a simple interface for term lookup and retrieval, hiding away the details of how the index is created and stored.
    There are NO methods for adding or removing postings from the index. InvertedIndex is read-only, and based off of data specified from `index_dir`.
    """

    def __init__(self, index_dir: Path) -> None:
        self._index_dir = index_dir
        self._index_fp = self._index_dir / "inverted_index.bin"
        self._doc_id_map_fp = self._index_dir / "doc_id_map.json"

        # needs initialization
        self._num_terms = 0
        self._num_postings = 0
        self._doc_id_to_url: dict[int, str] = {}
        if self._doc_id_map_fp.exists():
            with open(self._doc_id_map_fp, 'r') as f:
                # convert doc_ids back to int
                self._doc_id_to_url = {
                    int(k): v for k, v in json.load(f).items()}

    def _search_term(self, term: Term) -> PostingList:
        """Returns a list of postings for a given term."""
        with open(self._index_fp, "rb") as f:
            index = PartialIndex.deserialize(f.read())._index
            # return empty PostingList if term isnt found
            return index.get(term, PostingList())

    def retrieve(self, query: str) -> list[str | None]:
        """
        Given a query string, return a list of documents.
        """
        stemmed_terms = tokenize(query)

        posting_lists = []
        for term_str in stemmed_terms:
            term = Term(term_str)
            posting_list = self._search_term(term)
            if not posting_list._postings:
                # if term in terms not found, return empty list (because AND will return nothing)
                return []
            posting_lists.append(posting_list)

        result_doc_ids = set(
            posting.doc_id for posting in posting_lists[0]._postings)

        # intersect with the document IDs from the remaining posting lists
        for i in range(1, len(posting_lists)):
            next_doc_ids = set(
                posting.doc_id for posting in posting_lists[i]._postings)
            # updates set in place to contain only common elements
            result_doc_ids.intersection_update(next_doc_ids)

        # at this point result_doc_ids is a set of doc_ids that contain all terms in the query

        # convert doc_ids to urls
        retrieved_urls = [self._doc_id_to_url.get(
            doc_id) for doc_id in sorted(list(result_doc_ids))]

        return retrieved_urls[:5]  # return top 5

    def __str__(self):
        return f"<InvertedIndex stored at {self._index_dir} | {self._num_terms} terms, {self._num_postings} postings>"
