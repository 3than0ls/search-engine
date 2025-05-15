import unittest
import tempfile
from pathlib import Path
from index.inverted_index import InvertedIndex
from index.posting import Posting


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.ii_dir = tempfile.TemporaryDirectory()
        self.ii = InvertedIndex(self.ii_dir.name)

    def tearDown(self):
        self.ii_dir.cleanup()

    def test_add_posting(self):
        self.assertNotIn('test', self.ii._partial_index.keys())
        self.ii.add_posting('test', Posting('id1', 1))
        self.assertEqual(self.ii._partial_index['test']._postings, [
                         Posting('id1', 1)])
        self.assertIn('test', self.ii._partial_index.keys())

        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 1)

    def test_add_posting_in_order(self):
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]
        for posting in postings:
            self.ii.add_posting('test', posting)
        self.assertEqual(
            self.ii._partial_index['test']._postings, sorted(postings))
        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 4)

    def test_add_same_posting_twice(self):
        self.ii.add_posting('test', Posting('id1', 1))
        self.assertRaises(AssertionError, self.ii.add_posting,
                          'test', Posting('id1', 1))
        self.assertEqual(self.ii.num_terms(), 1)
        self.assertEqual(self.ii.num_postings(), 1)

    def test_dumps(self):
        for i in range(self.ii._BATCH_SIZE):
            self.ii.add_posting(str(i), Posting(f'id{i}', 1))
        self.assertEqual(self.ii.num_terms(), self.ii._BATCH_SIZE)
        self.assertTrue(list(Path(self.ii._partial_index_dir).iterdir()))
        self.assertTrue(len(self.ii._partial_index) == 0)

        self.ii.add_posting('test', Posting('id1', 1))
        self.assertTrue(len(self.ii._partial_index) == 1)
        self.assertEqual(self.ii.num_terms(), self.ii._BATCH_SIZE + 1)
        self.assertEqual(
            len(list(Path(self.ii._partial_index_dir).iterdir())), 1)

        with self.ii as index:
            index.add_posting('test2', Posting('id1', 1))
        # mimic real scenario where it's not a test and we dump
        self.ii._dump_partial_index()

        self.assertEqual(len(self.ii._partial_index), 0)
        self.assertEqual(
            len(list(Path(self.ii._partial_index_dir).iterdir())), 2)


if __name__ == '__main__':
    unittest.main()
