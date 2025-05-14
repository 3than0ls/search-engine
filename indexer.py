from utils import InvertedIndex, Posting, get_tokens
from bs4 import BeautifulSoup
import json
import glob
from pathlib import Path


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

        for token, count in tokens.items():
            posting = Posting(doc_id=doc_id, term_frequency=count)
            self._index.add_posting(token, posting)

        self._num_docs += 1

    def num_docs(self) -> int:
        return self._num_docs

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        for doc_path in self._webpages_dir.rglob('*.json'):
            self._process_document(doc_path)
            if self._num_docs > 1000:
                print('stopping early')
                break
        print(self)

    def __str__(self):
        return f"<Indexer for {self._webpages_dir} | {self._num_docs} documents>"
