import unittest

from index.posting_list import PostingList
from index.posting import Posting
from index.delimeters import POSTING_DELIMETER, POSTING_LIST_DELIMETER


class TestPosting(unittest.TestCase):
    def test_posting_serialize(self):
        posting = Posting('id1', 1)
        self.assertEqual(posting.serialize(),
                         POSTING_DELIMETER.join(['id1', '1']))  # will change

    def test_posting_ordering(self):
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]

        self.assertEqual(
            sorted(postings),
            [Posting('id1', 1), Posting('id2', 1),
             Posting('id3', 1), Posting('id4', 1)]
        )

    def test_posting_list_serialization(self):
        plist = PostingList()
        postings = [Posting('id4', 1), Posting('id2', 1),
                    Posting('id3', 1), Posting('id1', 1)]
        for posting in postings:
            plist.add_posting(posting)
        self.assertEqual(plist._postings, sorted(postings))
        self.assertEqual(plist.serialize(),
                         POSTING_LIST_DELIMETER.join([posting.serialize() for posting in sorted(postings)]))


if __name__ == '__main__':
    unittest.main()
