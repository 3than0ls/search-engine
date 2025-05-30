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
from index import Term, PostingList, Posting
from utils.tokenize import tokenize
import math
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
        # self._num_terms = 0
        # self._num_postings = 0
        self._num_docs = 0
        self._doc_id_to_url: dict[int, str] = {}
        if self._doc_id_map_fp.exists():
            with open(self._doc_id_map_fp, 'r') as f:
                # convert doc_ids back to int
                self._doc_id_to_url = {
                    int(k): v for k, v in json.load(f).items()}
            self._num_docs = len(self._doc_id_to_url)

    def _search_term(self, term: Term) -> PostingList:
        """Returns a list of postings for a given term."""
        with open(self._index_fp, "rb") as f:
            index = PartialIndex.deserialize(f.read())._index
            # return empty PostingList if term isnt found
            return index.get(term, PostingList())

    def _compute_tf_idf(self, term: Term, posting: Posting, term_posting_list: PostingList) -> float:
        """
        Compute the TF-IDF score for a term and a Posting (which represents a document in which that term is found in).
        """
        tf = 1 + math.log10(posting.term_frequency)
        # length of the term's posting list is the document frequency of that term. Add one to it in case the length is zero to avoid division by zero.
        idf = math.log10(self._num_docs / (1 + len(term_posting_list)))
        return tf * idf

    def _compute_score(self, term_postings: dict[Term, PostingList], posting: Posting) -> float:
        """
        Future optimization: only compute scores for postings that are in ALL term posting lists:
        Essentially do a boolean retrieval first, then compute scores for the remaining postings.
        """
        score = 0
        for term, posting_list in term_postings.items():
            score += self._compute_tf_idf(term, posting, posting_list)
        return score

    def _retrieve(self, query: str) -> dict[Term, PostingList]:
        """
        Given a query string, return a dictionary mapping each term in the query to their entire posting lists.
        """
        stemmed_terms = tokenize(query)

        posting_lists = {}
        for term_str in stemmed_terms:
            term = Term(term_str)
            posting_list = self._search_term(term)
            posting_lists[Term] = posting_list

        return posting_lists

    def ranked_retrieve(self, query: str) -> list[str | None]:
        """
        Given a query string, return a list of documents using TD-IDF ranked retrieval.
        """
        posting_lists = self._retrieve(query)

        # to get all documents that could potentially match the query, we need to flatten posting_lists
        all_postings = [
            posting
            for posting_list in posting_lists.values()
            for posting in posting_list
        ]

        results: list[tuple[int, float]] = []
        for posting in all_postings:
            score = self._compute_score(posting_lists, posting)
            results.append((posting.doc_id, score))

        # sort results by score in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        print(results[:5])

        return [self._doc_id_to_url.get(result[0]) for result in results[:5]]

    def bool_retrieve(self, query: str) -> list[str | None]:
        """
        Given a query string, return a list of documents using boolean retrieval.
        """
        # for boolean retrieval, we don't need to care about the actual terms themselves, just posting lists
        posting_lists = list(self._retrieve(query).values())

        # optimization: if any of the posting lists are empty, then boolean retrieval should return no results
        if not all(posting_lists):
            return []

        result_doc_ids = set(
            posting.doc_id for posting in posting_lists[0])

        # intersect with the document IDs from the remaining posting lists
        for i in range(1, len(posting_lists)):
            next_doc_ids = set(
                posting.doc_id for posting in posting_lists[i])
            # updates set in place to contain only common elements
            result_doc_ids.intersection_update(next_doc_ids)

        # at this point result_doc_ids is a set of doc_ids that contain all terms in the query

        # convert doc_ids to urls
        retrieved_urls = [self._doc_id_to_url.get(
            doc_id) for doc_id in sorted(list(result_doc_ids))]

        return retrieved_urls[:5]  # return top 5

    def __str__(self):
        return f"<InvertedIndex stored at {self._index_dir} | {self._num_docs} documents>"
