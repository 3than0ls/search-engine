import unittest
import tempfile
from pathlib import Path
from engine.inverted_index import InvertedIndex
from index import Indexer, Term, Posting
from utils import load_config


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.pi_dir = tempfile.TemporaryDirectory()
        indexer = Indexer(Path('./unittests'),
                          Path(self.pi_dir.name), Path(self.ii_dir.name))
        indexer.construct()
        self.index = InvertedIndex(Path(self.ii_dir.name))

    def tearDown(self):
        self.ii_dir.cleanup()
        self.pi_dir.cleanup()

    def test_search_term_returns(self):
        results = self.index._search_term(Term('foo'))
        oracle = [
            Posting(1, 6),
            Posting(2, 3)
        ]
        for i, result in enumerate(results):
            self.assertEqual(result, oracle[i])


if __name__ == '__main__':
    unittest.main()
