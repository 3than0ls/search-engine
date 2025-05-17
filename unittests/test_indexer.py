import unittest

from index.inverted_index import InvertedIndex
from index.posting import Posting
from index.indexer import Indexer
from pathlib import Path
import tempfile
from utils import load_config


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.pi_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.ii_dir.cleanup()
        self.pi_dir.cleanup()

    def create_ii(self, _):
        return InvertedIndex(Path(self.ii_dir.name))

    def test_load_doc(self):
        indexer = Indexer(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        content, url, encoding = indexer._load_document(
            Path('./unittests/doc_id_1.json'))

        self.assertEqual(content, 'foo foo foo foo foo foo bar bar bar baz')
        self.assertEqual(url, 'foo.com')
        self.assertEqual(encoding, 'utf-8')

    def test_process_doc(self):
        indexer = Indexer(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer._process_document(Path('./unittests/doc_id_1.json'))
        self.assertEqual(indexer.num_docs(), 1)
        indexer._process_document(Path('./unittests/doc_id_2.json'))
        self.assertEqual(indexer.num_docs(), 2)

    def test_construct_partial_index(self):
        indexer = Indexer(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer._construct_partial_indexes()
        self.assertEqual(indexer._partial_index_count, 1)
        self.assertEqual(
            len(list(Path(self.pi_dir.name).iterdir())), 1
        )
        self.assertEqual(
            indexer._partial_index._index['foo']._postings,
            [Posting('doc_id_1', 6), Posting('doc_id_2', 3)])
        self.assertEqual(
            indexer._partial_index._index['bar']._postings,
            [Posting('doc_id_1', 3), Posting('doc_id_2', 6)])
        self.assertEqual(
            indexer._partial_index._index['baz']._postings,
            [Posting('doc_id_1', 1), Posting('doc_id_2', 1)])

    def test_merge(self):
        indexer = Indexer(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer._construct_partial_indexes()
        indexer._merge_partial_indexes()
        path = Path(self.ii_dir.name)
        self.assertTrue(path.exists())
        self.assertTrue((path / 'index.txt').exists())
        self.assertTrue((path / 'terms.txt').exists())
        self.assertEqual(
            len(list(path.iterdir())), 2
        )


if __name__ == '__main__':
    unittest.main()
