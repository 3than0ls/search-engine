import unittest

from index.posting_list import PostingList
from index.posting import Posting
from index.term import Term


class TestPosting(unittest.TestCase):
    def test_term_serialize(self):
        term = Term('hello')
        self.assertEqual(Term.deserialize(term.serialize()), term)

    def test_posting_serialize(self):
        posting = Posting(1, 1)
        self.assertEqual(Posting.deserialize(posting.serialize()), posting)
        posting = Posting(5, 6)
        self.assertEqual(Posting.deserialize(posting.serialize()), posting)
        posting = Posting(2, 4)
        self.assertEqual(Posting.deserialize(posting.serialize()), posting)
        posting = Posting(71231237, 1123122)
        self.assertEqual(Posting.deserialize(posting.serialize()), posting)

    def test_posting_ordering(self):
        postings = [Posting(4, 1), Posting(2, 1),
                    Posting(3, 1), Posting(1, 1)]

        self.assertEqual(
            sorted(postings),
            [Posting(1, 1), Posting(2, 1),
             Posting(3, 1), Posting(4, 1)]
        )

    def test_posting_list_serialization(self):
        plist = PostingList()
        postings = [Posting(4, 1), Posting(2, 1),
                    Posting(3, 1), Posting(1, 1)]
        for posting in postings:
            plist.add_posting(posting)
        self.assertEqual(plist._postings, sorted(postings))
        self.assertEqual(PostingList.deserialize(plist.serialize()), plist)

    def test_posting_list_yield(self):
        plist = PostingList()
        postings = [Posting(4, 1), Posting(2, 1),
                    Posting(3, 1), Posting(1, 1)]
        for posting in postings:
            plist.add_posting(posting)

        posting_sorted = sorted(postings)
        for i, posting in enumerate(plist):
            self.assertEqual(posting, posting_sorted[i])


if __name__ == '__main__':
    unittest.main()
