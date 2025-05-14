from utils import InvertedIndex, Posting, get_tokens
from bs4 import BeautifulSoup
import json
from pathlib import Path


class Indexer:
    def __init__(self, webpages_dir='./ANALYST'):
        self._index = InvertedIndex()
        self._webpages_dir = webpages_dir

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

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        pass
