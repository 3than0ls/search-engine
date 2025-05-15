import unittest

from index.inverted_index import InvertedIndex
from index.posting import Posting
from index.indexer import Indexer
from pathlib import Path
import tempfile


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.ii_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.ii_dir.cleanup()

    def create_test_ii(self):
        return InvertedIndex(partial_index_dir=self.ii_dir.name)

    def test_construct(self):
        indexer = Indexer(
            Path('./unittests'),
            _inverted_index_factory=self.create_test_ii)  # type: ignore
        indexer.construct()
        self.assertEqual(
            indexer._index._partial_index['foo']._postings,
            [Posting('doc_id_1', 6), Posting('doc_id_2', 3)])
        self.assertEqual(
            indexer._index._partial_index['bar']._postings,
            [Posting('doc_id_1', 3), Posting('doc_id_2', 6)])
        self.assertEqual(
            indexer._index._partial_index['baz']._postings,
            [Posting('doc_id_1', 1), Posting('doc_id_2', 1)])
        self.assertEqual(indexer.num_docs(), 2)
        self.assertEqual(indexer._index.num_terms(), 3)
        self.assertEqual(indexer._index.num_postings(), 6)
        indexer._index._dump_partial_index()
        # explore
        # import time
        # time.sleep(15)


if __name__ == '__main__':
    unittest.main()
