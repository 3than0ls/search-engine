import unittest
import shelve
import tempfile
import os
import glob

from utils.inverted_index import InvertedIndex
from utils.posting import Posting

SHELVE_NAME = "test.shelve"


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ii_fp = os.path.join(self.temp_dir.name, SHELVE_NAME)
        self.ii = InvertedIndex(self.ii_fp)

    def tearDown(self):
        for file in glob.glob(self.ii_fp + '*'):
            os.remove(file)
        self.temp_dir.cleanup()

    def test_add_posting(self):
        self.assertNotIn('test', self.ii._current_batch.keys())
        self.ii.add_posting('test', Posting('id1', 1))
        self.assertEqual(self.ii._current_batch['test'], [Posting('id1', 1)])
        self.assertIn('test', self.ii._current_batch.keys())

        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 1)

    def test_add_posting_in_order(self):
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]
        for posting in postings:
            self.ii.add_posting('test', posting)
        self.assertEqual(self.ii._current_batch['test'], sorted(postings))
        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 4)

    def test_add_same_posting_twice(self):
        self.ii.add_posting('test', Posting('id1', 1))
        self.assertRaises(AssertionError, self.ii.add_posting,
                          'test', Posting('id1', 1))
        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 1)


if __name__ == '__main__':
    unittest.main()
