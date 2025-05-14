import unittest

from utils.inverted_index import InvertedIndex
from utils.posting import Posting


class TestPosting(unittest.TestCase):
    def test_ordering(self):
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]

        self.assertEqual(
            sorted(postings),
            [Posting('id1', 1), Posting('id2', 1),
             Posting('id3', 1), Posting('id4', 1)]
        )


if __name__ == '__main__':
    unittest.main()
