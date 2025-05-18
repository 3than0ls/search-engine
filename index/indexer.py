from index.term import Term
from index.partial_index import PartialIndex
from index.posting import Posting
from utils import get_tokens, index_log
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import json
from pathlib import Path
import os
import warnings
from collections import Counter
import time

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


class Indexer:
    """
    Indexes a directory of webpages downloaded from project specifications.
    Stores partial indexes to disk, the polyphase merges them at the end.

    This class should be a singleton; it will only be created and constructed once per program execution.
    """

    def __init__(self, webpages_dir: Path, partial_index_dir: Path, index_dir: Path):
        # validate directories
        if not webpages_dir.is_dir():
            raise ValueError(
                f"Webpages directory {webpages_dir} is not a valid directory.")
        if partial_index_dir.is_dir() and partial_index_dir.exists() and any(partial_index_dir.iterdir()):
            raise ValueError(
                f"Partial index directory must be empty.")
        partial_index_dir.mkdir(exist_ok=True)
        if index_dir.is_dir() and index_dir.exists() and any(index_dir.iterdir()):
            raise ValueError(f"Index directory must be empty.")
        index_dir.mkdir(exist_ok=True)

        self._webpages_dir = webpages_dir
        self._partial_index_dir = partial_index_dir
        self._index_dir = index_dir

        # track statistics to output at the end
        self._num_docs = 0
        self._num_terms = 0
        self._start_time = 0

        # mapping of document IDs (int) to document paths (Path)
        self._doc_id_map: dict[int, Path] = {}

        # data for partial indexing- dangerous to modify during indexing, constant changes as construction goes on
        self._BATCH_SIZE = 2 ** 18
        self._partial_index_count = 0
        self._partial_index = PartialIndex()

    def _load_document(self, doc_path: Path) -> tuple[str, str, str]:
        """Literally just a loader wrapper, but with some assertion checks that I KNOW will pass."""
        with open(doc_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # this 100% should already exist; we assume downloaded data is in correct JSON format
        assert 'content' in data, f"Content not specified for {doc_path}"
        content = data['content']
        assert 'url' in data, f"URL not specified for {doc_path}"
        url = data['url']
        assert 'encoding' in data, f"Encoding not specified for {doc_path}"
        encoding = data['encoding']

        return content, url, encoding

    def _process_document(self, doc_path: Path) -> Counter[str]:
        """Literally just a tokenizer wrapper, but also increases a _num_docs counter."""
        content, url, _ = self._load_document(doc_path)
        soup = BeautifulSoup(content, 'html.parser')
        tokens = get_tokens(soup.get_text(separator=" ", strip=True))

        # could use our own custom hashing of URL, but I'll pass
        # doc_id = doc_path.stem
        # index_log.info(
        #     f"Processed [{doc_id}]({url}), and updating the index with {len(tokens)} postings.")

        self._num_docs += 1
        return tokens

    def _dump_current_partial_index(self):
        """Serialize current partial index to disk. Used in `self._create_new_partial_index()`"""
        self._partial_index_dir.mkdir(exist_ok=True)
        fname = f"partial_index_{self._partial_index_count:03}.bin"
        path = self._partial_index_dir / fname

        index_log.info(f"Dumping current partial index to {path}")

        start = time.time()
        serialization = self._partial_index.serialize()
        end = time.time()
        index_log.info(
            f"Serializing current partial index {path} took {(end - start):.2f}s")

        start = time.time()
        with open(path, 'wb') as f:
            f.write(serialization)
        end = time.time()
        index_log.info(
            f"Writing current partial index {path} took {(end - start):.2f}s")

    def _create_new_partial_index(self):
        """Sets the _partial_index attribute to a new PartialIndex object, done when needing to dump old partial index and start anew."""
        self._dump_current_partial_index()
        self._partial_index_count += 1
        self._partial_index = PartialIndex()

    def _construct_partial_indexes(self) -> None:
        """Constructs partial indexes from a directory of webpages."""
        for doc_path in self._webpages_dir.rglob('*.json'):
            tokens = self._process_document(doc_path)
            self._doc_id_map[self._num_docs] = doc_path
            for token, count in tokens.items():
                posting = Posting(doc_id=self._num_docs,
                                  term_frequency=count)
                self._partial_index.add_posting(Term(token), posting)

                if self._partial_index.num_postings() >= self._BATCH_SIZE:
                    self._create_new_partial_index()

                self._num_terms += 1

        # dump the last partial index if there's anything left over. don't bother resetting it with a new partial index
        if self._partial_index.num_postings() > 0:
            self._dump_current_partial_index()
            self._partial_index_count += 1

    def _partial_index_read_line(self) -> None:
        pass
        # with open()

    def _merge_partial_indexes(self) -> None:
        """
        Merges all partial indexes into a single InvertedIndex object.
        Partial indexes are stored in self._partial_index_dir directory. 
        Should not be called before first constructing the partial indexes.
        """
        # self._index = merge(self._partial_index_dir, self._index_dir)
        raise NotImplementedError

    def num_docs(self) -> int:
        return self._num_docs

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        index_log.info(f"Indexing documents from {self._webpages_dir}")

        index_start_time = time.time()
        self._construct_partial_indexes()
        index_finish_time = time.time()

        # mundane logging
        index_log.info(
            f"Finished indexing all documents and created object {self}")
        partial_index_size = sum(f.stat().st_size for f in self._partial_index_dir.glob(
            '**/*') if f.is_file()) / 1024
        summary = f"Indexer summary:\n"
        summary += \
            f"Number of indexed documents: {self._num_docs}\n" + \
            f"Number of unique tokens: {self._num_terms}\n" + \
            f"Total size of partial indexes on disk: {f"{partial_index_size}KB at {self._partial_index_dir}" or "NOT FOUND"}\n" + \
            f"Time elapsed (indexing): {(index_finish_time - index_start_time):.2f}s"
        print("-"*80)
        print(summary)
        index_log.info(summary)

        merge_start_time = time.time()
        self._merge_partial_indexes()
        merge_finish_time = time.time()

        # more logging
        index_log.info(
            f"Finished merging all partial indexes.")
        index_size = sum(f.stat().st_size for f in self._index_dir.glob(
            '**/*') if f.is_file()) / 1024
        summary = \
            f"Total size of inverted index on disk: {f"{index_size}KB at {self._partial_index_dir}" or "NOT FOUND"}\n" + \
            f"Time elapsed (merge): {(merge_finish_time - merge_start_time):.2f}s" + \
            f"Time elapsed (total): {(merge_finish_time - index_start_time):.2f}s"
        print(summary)
        index_log.info(summary)
        print("-"*80)

    def __str__(self):
        return f"<Indexer for {self._webpages_dir} | {self._num_docs} documents>"
