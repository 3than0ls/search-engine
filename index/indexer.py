from index.inverted_index import InvertedIndex
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
    Stores it in InvertedIndex.
    """

    def __init__(self, webpages_dir, *, _inverted_index_factory=InvertedIndex):
        if not Path(webpages_dir).is_dir():
            raise ValueError(
                f"Webpages directory {webpages_dir} is not a valid directory.")

        self._index = _inverted_index_factory()
        self._webpages_dir = Path(webpages_dir)

        self._num_docs = 0

        self._start_time = 0

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

    def _process_document(self, doc_path: Path) -> Counter:
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

    def num_docs(self) -> int:
        return self._num_docs

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        index_log.info(f"Indexing documents from {self._webpages_dir}")
        start_time = time.time()

        with self._index as index:
            for doc_path in self._webpages_dir.rglob('*.json'):
                tokens = self._process_document(doc_path)
                for token, count in tokens.items():
                    posting = Posting(doc_id=doc_path.stem,
                                      term_frequency=count)
                    index.add_posting(token, posting)

        # mundane logging
        index_log.info(
            f"Finished indexing all documents and created object {self}")
        out_dir = self._index._partial_index_dir
        index_size = sum(f.stat().st_size for f in out_dir.glob(
            '**/*') if f.is_file()) / 1024
        summary = f"Index summary:\n" + \
            f"Number of indexed documents: {self._num_docs}\n" + \
            f"Number of unique tokens: {self._index.num_terms()}\n" + \
            f"Total size of index(es) on disk: {f"{index_size}KB at {out_dir}" or "NOT FOUND"}\n" + \
            f"Time elapsed: {(time.time() - start_time):.2f}s"
        index_log.info(summary)
        print("-"*80)
        print(summary)
        print("-"*80)

    def __str__(self):
        return f"<Indexer for {self._webpages_dir} | {self._num_docs} documents>"
