import unittest

from index.posting import Posting
from index.term import Term
from index.indexer import Indexer
from pathlib import Path
import tempfile
from utils import load_config
from index.partial_index import PartialIndexBuilder


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.pi_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.ii_dir.cleanup()
        self.pi_dir.cleanup()

    def test_load_doc(self):
        indexer = PartialIndexBuilder(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        content, url, encoding = indexer._load_document(
            Path('./unittests/0.json'))

        self.assertEqual(content, 'foo foo foo foo foo foo bar bar bar baz')
        self.assertEqual(url, 'foo.com')
        self.assertEqual(encoding, 'utf-8')

    def test_process_doc(self):
        indexer = PartialIndexBuilder(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer._process_document(Path('./unittests/0.json'))
        self.assertEqual(indexer._num_docs, 1)
        indexer._process_document(Path('./unittests/1.json'))
        self.assertEqual(indexer._num_docs, 2)

    def test_construct_partial_index(self):
        indexer = PartialIndexBuilder(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer.build()
        self.assertEqual(indexer._partial_index_count, 1)
        self.assertEqual(
            len(list(Path(self.pi_dir.name).iterdir())), 1
        )
        doc_1_id = 1 - 1
        doc_2_id = 2 - 1
        self.assertEqual(
            indexer._partial_index._index[Term('foo')]._postings,
            [Posting(doc_1_id, 6), Posting(doc_2_id, 3)])
        self.assertEqual(
            indexer._partial_index._index[Term('bar')]._postings,
            [Posting(doc_1_id, 3), Posting(doc_2_id, 6)])
        self.assertEqual(
            indexer._partial_index._index[Term('baz')]._postings,
            [Posting(doc_1_id, 1), Posting(doc_2_id, 1)])

    def test_merge(self):
        indexer = Indexer(
            Path('./unittests'),
            Path(self.pi_dir.name),
            Path(self.ii_dir.name))
        indexer._build_partial_indexes()
        indexer._merge_partial_indexes()
        path = Path(self.ii_dir.name)
        self.assertTrue(path.exists())
        self.assertTrue((path / 'inverted_index.bin').exists())
        self.assertTrue((path / 'terms_map.bin').exists())
        self.assertTrue((path / 'document_map.bin').exists())
        self.assertEqual(
            len(list(path.iterdir())), 2
        )


if __name__ == '__main__':
    unittest.main()
