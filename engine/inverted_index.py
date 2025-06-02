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
import struct
from index.term import TERM_LENGTH_FORMAT, TERM_LENGTH_SIZE
from index.posting_list import POSTING_LIST_LENGTH_FORMAT, POSTING_LIST_LENGTH_SIZE
from index.posting import POSTING_SIZE


class InvertedIndex:
    """
    The inverted index is a mapping of index terms (`str`) to postings PostingList (`PostingList`).

    This class is used to provide a simple interface for term lookup and retrieval, hiding away the details of how the index is created and stored.
    There are NO methods for adding or removing postings from the index. InvertedIndex is read-only, and based off of data specified from `index_dir`.
    """

    def __init__(self, index_dir: Path) -> None:
        self._index_dir = index_dir

        if not index_dir.is_dir() or not index_dir.exists() or not any(index_dir.iterdir()):
            raise ValueError(
                f"Inverted index directory must be exist and be populated.")

        self._index_fp = self._index_dir / "inverted_index.bin"
        self._doc_id_map_fp = self._index_dir / "doc_id_map.json"
        self._term_to_ii_position_fp = self._index_dir / "term_to_ii_position.json"

        with open(self._doc_id_map_fp, 'r') as f:
            # convert doc_ids back to int
            self._doc_id_to_url = {
                int(doc_id): doc_url for doc_id, doc_url in json.load(f).items()}
            self._num_docs = len(self._doc_id_to_url)

        with open(self._term_to_ii_position_fp, 'r') as f:
            # convert term_to_ii_position to dict[str, int]
            self._term_to_ii_position = {
                term: pos for term, pos in json.load(f).items()}
            self._num_terms = len(self._term_to_ii_position)

        print("Number of documents in index:", self._num_docs)
        print("Number of terms in index:", self._num_terms)

    def _search_term(self, term: Term) -> PostingList:
        """Returns a list of postings for a given term."""
        with open(self._index_fp, "rb") as f:
            position = self._term_to_ii_position.get(term.term)
            if position is None:
                # return empty PostingList if term isn't found in term to inverted index mapping
                return PostingList()
            f.seek(position)

            # super shit design; I designed deserialization in PostingList and Post for partial index creation and merging
            # that was designed to read a variable length of bytes and produce the object from it
            # did not design it for a buffered reader. and if we were to convert the buffered reader into a bytes we'd have to load the entire thing
            # instead, we have to basically reimplement deserialization, but instead of using a fixed bytes, we use the buffered reader
            # I hate this this sucks
            term_length = struct.unpack(
                TERM_LENGTH_FORMAT, f.read(TERM_LENGTH_SIZE))[0]
            term_data = f.read(term_length)
            str_term = term_data.decode("utf-8")
            assert str_term == term.term, "Term mismatch"

            byte_buffer = f.read(POSTING_LIST_LENGTH_SIZE)
            posting_list_length = struct.unpack(
                POSTING_LIST_LENGTH_FORMAT, byte_buffer)[0]
            byte_buffer += f.read(posting_list_length * POSTING_SIZE)
            posting_list = PostingList.deserialize(byte_buffer)
            return posting_list

    def _compute_tf_idf(self, term: Term, posting: Posting, term_posting_list: PostingList) -> float:
        """
        Compute the TF-IDF score for a term and a Posting (which represents a document in which that term is found in).
        """
        tf = 1 + math.log10(posting.term_frequency)
        # length of the term's posting list is the document frequency of that term. Add one to it in case the length is zero to avoid division by zero.
        idf = math.log10(self._num_docs / len(term_posting_list))
        return tf * idf

    def _compute_score(self, term_postings: dict[Term, PostingList], posting: Posting) -> float:
        """
        Term postings are a dictionary of all terms in the query and their corresponding posting lists.
        Future optimization: only compute scores for postings that are in ALL term posting lists:
        Essentially do a boolean retrieval first, then compute scores for the remaining postings.

        Additionally, implements the soft conjunction heuristic. If the query has multiple terms, but several are not found in the document, don't include it.
        The threshold for "several" is set to 3/4ths of the number of terms in the query.
        """

        query_len = len(term_postings)
        num_terms = 0
        score = 0
        for term, posting_list in term_postings.items():
            if len(posting_list) == 0:
                continue
            score += self._compute_tf_idf(term, posting, posting_list)
            num_terms += 1

        if num_terms <= query_len * 0.75:
            return 0.0

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
        # print(results[:5])

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
