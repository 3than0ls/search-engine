import unittest
from index.partial_index.partial_index import PartialIndex
from index.term import Term
from index.posting import Posting


class TestPartialIndex(unittest.TestCase):
    def setUp(self):
        self.pi = PartialIndex()

    def test_add_posting(self):
        term_test = Term('test')
        self.assertNotIn(term_test, self.pi._index.keys())
        self.pi.add_posting(term_test, Posting(1, 1))
        self.assertEqual(self.pi._index[term_test]._postings,
                         [Posting(1, 1)])
        self.assertIn(term_test, self.pi._index.keys())

        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 1)

    def test_add_posting_in_order(self):
        term_test = Term('test')
        postings = [Posting(4, 1), Posting(2, 1),
                    Posting(3, 1), Posting(1, 1)]
        for posting in postings:
            self.pi.add_posting(term_test, posting)
        self.assertEqual(
            self.pi._index[term_test]._postings, sorted(postings))
        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 4)

    def test_add_same_posting_twice(self):
        term_test = Term('test')
        self.pi.add_posting(term_test, Posting(1, 1))
        self.assertRaises(AssertionError, self.pi.add_posting,
                          term_test, Posting(1, 1))
        self.assertEqual(self.pi.num_terms(), 1)
        self.assertEqual(self.pi.num_postings(), 1)

    def test_simple_serialization(self):
        self.pi.add_posting(Term('test'), Posting(1, 1))
        self.assertEqual(PartialIndex.deserialize(
            self.pi.serialize()), self.pi)

    def test_simple_serialization_2(self):
        self.pi.add_posting(Term('test'), Posting(1, 1))
        self.pi.add_posting(Term('test2'), Posting(2, 2))
        self.assertEqual(PartialIndex.deserialize(
            self.pi.serialize()), self.pi)

    def test_serialization(self):
        sample_postings = [Posting(4, 1), Posting(
            2, 1), Posting(3, 1), Posting(1, 1)]
        for i in range(100):
            for posting in sample_postings:
                self.pi.add_posting(Term(f'test{i}'), posting)
        self.assertEqual(PartialIndex.deserialize(
            self.pi.serialize()), self.pi)


if __name__ == '__main__':
    unittest.main()
