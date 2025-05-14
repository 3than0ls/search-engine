import unittest

from utils.inverted_index import InvertedIndex
from utils.posting import Posting
from indexer import Indexer


class TestInvertedIndex(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
