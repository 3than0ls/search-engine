import unittest
import tempfile
from pathlib import Path
from index.partial_index import PartialIndex
from index.posting import Posting
from utils import load_config


class TestPartialIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.pi = PartialIndex(0, Path(self.ii_dir.name))

    def tearDown(self):
        self.ii_dir.cleanup()

    def test_add_posting(self):
        self.assertNotIn('test', self.pi._index.keys())
        self.pi.add_posting('test', Posting('id1', 1))
        self.assertEqual(self.pi._index['test']._postings, [
                         Posting('id1', 1)])
        self.assertIn('test', self.pi._index.keys())

        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 1)

    def test_add_posting_in_order(self):
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]
        for posting in postings:
            self.pi.add_posting('test', posting)
        self.assertEqual(
            self.pi._index['test']._postings, sorted(postings))
        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 4)

    def test_add_same_posting_twice(self):
        self.pi.add_posting('test', Posting('id1', 1))
        self.assertRaises(AssertionError, self.pi.add_posting,
                          'test', Posting('id1', 1))
        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 1)

    def test_dumps(self):
        for i in range(100):
            self.pi.add_posting(str(i), Posting(f'id{i}', 1))
        self.pi.dump()
        self.assertTrue(list(Path(self.pi._partial_index_dir).iterdir()))


if __name__ == '__main__':
    unittest.main()
