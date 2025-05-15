import unittest

from index.inverted_index import InvertedIndex
from index.posting import Posting
from index.indexer import Indexer
import tempfile
import os
import glob


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ii_fp = os.path.join(self.temp_dir.name, "test.shelve")

    def tearDown(self):
        for file in glob.glob(self.ii_fp + '*'):
            os.remove(file)
        self.temp_dir.cleanup()

    def test_process_document(self):
        indexer = Indexer()
        indexer._process_document('./unittests/doc_id_1.json')
        self.assertEqual(
            indexer._index._current_batch['foo'],
            [Posting('doc_id_1', 6)])
        self.assertEqual(
            indexer._index._current_batch['bar'],
            [Posting('doc_id_1', 3)])
        self.assertEqual(
            indexer._index._current_batch['baz'],
            [Posting('doc_id_1', 1)])

    def test_process_two_documents(self):
        indexer = Indexer()
        indexer._process_document('./unittests/doc_id_1.json')
        indexer._process_document('./unittests/doc_id_2.json')
        self.assertEqual(
            indexer._index._current_batch['foo'],
            [Posting('doc_id_1', 6), Posting('doc_id_2', 3)])
        self.assertEqual(
            indexer._index._current_batch['bar'],
            [Posting('doc_id_1', 3), Posting('doc_id_2', 6)])
        self.assertEqual(
            indexer._index._current_batch['baz'],
            [Posting('doc_id_1', 1), Posting('doc_id_2', 1)])

    def test_construct(self):
        indexer = Indexer(
            './unittests', _inverted_index_factory=lambda: InvertedIndex(fp=self.ii_fp))
        indexer.construct()
        self.assertEqual(indexer.num_docs(), 2)
        self.assertEqual(indexer._index.num_terms(), 3)
        self.assertEqual(indexer._index.num_postings(), 6)
        indexer._index.sync()


if __name__ == '__main__':
    unittest.main()
