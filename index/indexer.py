from index.inverted_index import InvertedIndex
from index.posting import Posting
from utils import get_tokens, index_log
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import json
from pathlib import Path
import os
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class Indexer:
    def __init__(self, webpages_dir='./ANALYST', *, _inverted_index_factory=InvertedIndex):
        self._index = _inverted_index_factory()
        self._webpages_dir = Path(webpages_dir)

        self._num_docs = 0

    def _load_document(self, doc_path: str) -> list[str, str, str]:
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

    def _process_document(self, doc_path: str) -> None:
        content, url, encoding = self._load_document(doc_path)
        # could use our own custom hashing of URL, but I'll pass
        doc_id = Path(doc_path).stem

        soup = BeautifulSoup(content, 'html.parser')
        tokens = get_tokens(soup.get_text(separator=" ", strip=True))

        index_log.info(
            f"Processed [{doc_id}]({url}), and updating the index with {len(tokens)} postings.")

        for token, count in tokens.items():
            posting = Posting(doc_id=doc_id, term_frequency=count)
            self._index.add_posting(token, posting)

        self._num_docs += 1

    def num_docs(self) -> int:
        return self._num_docs

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        index_log.info(f"Indexing documents from {self._webpages_dir}")

        for doc_path in self._webpages_dir.rglob('*.json'):
            self._process_document(doc_path)

        # sync the index one more time once done processing to save anything in the current batch
        self._index.sync()

        index_log.info(
            f"Finished indexing all documents and created object {self}")

        index_size = 0 if not os.path.exists(
            self._index._fp) else os.path.getsize(self._index._fp) / 1024
        summary = f"Index summary:\n" + \
            f"Number of indexed documents: {self._num_docs}\n" + \
            f"Number of unique tokens: {self._index.num_terms()}\n" + \
            f"Total size of index on disk: {f"{index_size}KB at {self._index._fp}" or "NOT FOUND"}"
        index_log.info(summary)
        print(summary)

    def __str__(self):
        return f"<Indexer for {self._webpages_dir} | {self._num_docs} documents>"
