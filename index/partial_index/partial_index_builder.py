from index.term import Term
from index.partial_index import PartialIndex
from index.term import Term
from index.posting_list import PostingList
from index.posting import Posting
from utils import get_postings, index_log
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Mapping
import time


class PartialIndexBuilder:
    def __init__(self, webpages_dir: Path, partial_index_dir: Path, index_dir: Path):
        self._webpages_dir = webpages_dir
        self._partial_index_dir = partial_index_dir
        self._index_dir = index_dir

        # track statistics to output at the end
        self._num_docs = 0
        self._num_terms = 0
        self._start_time = 0

        # mapping of document IDs (int) to document URLs, not paths
        self._doc_id_map: dict[int, str] = {}

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
        # project specs: ignore the fragment part, if you see it
        url = data['url'].split('#')[0]
        assert 'encoding' in data, f"Encoding not specified for {doc_path}"
        encoding = data['encoding']

        return content, url, encoding

    def _process_document(self, doc_path: Path) -> Mapping[Term, PostingList]:
        """Literally just a tokenizer wrapper, but also increases a _num_docs counter."""
        content, url, _ = self._load_document(doc_path)
        soup = BeautifulSoup(content, 'html.parser')
        # utilize the document number as the doc_id
        postings = get_postings(self._num_docs, soup)

        if self._num_docs not in self._doc_id_map and url not in self._doc_id_map.values():
            self._doc_id_map[self._num_docs] = url

        self._num_docs += 1
        return postings

    def _dump_current_partial_index(self) -> None:
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

    def _create_new_partial_index(self) -> None:
        """Sets the _partial_index attribute to a new PartialIndex object, done when needing to dump old partial index and start anew."""
        self._dump_current_partial_index()
        self._partial_index_count += 1
        self._partial_index = PartialIndex()

    def build(self) -> None:
        """Constructs partial indexes from a directory of webpages."""
        for doc_path in self._webpages_dir.rglob('*.json'):
            postings = self._process_document(doc_path)
            for term, postings_list in postings.items():
                self._partial_index.add_posting_list(term, postings_list)

                if self._partial_index.num_postings() >= self._BATCH_SIZE:
                    self._create_new_partial_index()

                self._num_terms += 1

        # dump the last partial index if there's anything left over. don't bother resetting it with a new partial index
        if self._partial_index.num_postings() > 0:
            self._dump_current_partial_index()
            self._partial_index_count += 1

        doc_id_map_fp = self._index_dir / "doc_id_map.json"
        with open(doc_id_map_fp, 'w') as f:
            json.dump(self._doc_id_map, f, indent=4)
        index_log.info(f"Saved document ID to URL mapping to {doc_id_map_fp}")
