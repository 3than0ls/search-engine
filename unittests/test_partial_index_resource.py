import unittest

from index.partial_index.partial_index import PartialIndex, PartialIndexResource
from index.posting import Posting
from index.posting_list import PostingList
from index.term import Term
from index.indexer import Indexer
from pathlib import Path
import tempfile
from utils import load_config


class TestPartialIndexResource(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.pi_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.ii_dir.cleanup()
        self.pi_dir.cleanup()

    def construct_pi(self):
        indexer = Indexer(Path('./unittests'), Path(self.pi_dir.name),
                          Path(self.ii_dir.name))
        indexer._build_partial_indexes()

    def construct_custom_pi(self) -> PartialIndex:
        pi = PartialIndex()
        left_postings = {
            "term1": [Posting(1, 1), Posting(3, 2), Posting(5, 3)],
            "term2": [Posting(100, 100)]
        }
        right_postings = {
            "term1": [Posting(2, 2), Posting(
                4, 3), Posting(6, 4), Posting(8, 5)],
            "term3": [Posting(200, 200)]
        }

        for key, posting_list in left_postings.items():
            for posting in posting_list:
                pi.add_posting(Term(key), posting)
        for key, posting_list in right_postings.items():
            for posting in posting_list:
                pi.add_posting(Term(key), posting)

        with open(Path(self.pi_dir.name) / 'out.bin', 'wb') as f:
            f.write(pi.serialize())

        with open(Path(self.pi_dir.name) / 'out.bin', 'rb') as f:
            out = PartialIndex.deserialize(f.read())
            self.assertEqual(out.num_postings(), pi.num_postings())
            self.assertEqual(out, pi)

        return pi

    def test_custom_pir(self):
        # construct partial indexes and serialize
        pi = self.construct_custom_pi()
        with PartialIndexResource(Path(self.pi_dir.name) / 'out.bin') as f:
            i = 0
            while item := f.read_item():
                term, posting_list = item
                self.assertEqual(term, pi._sorted_terms[i])
                self.assertEqual(posting_list, pi._index[term])
                i += 1

    def test_pir(self):
        # this test has to do with actual hardcoded values, and will fail later when we change Posting, can comment it out then,
        self.construct_pi()
        with PartialIndexResource(Path(self.pi_dir.name) / 'partial_index_000.bin') as f:
            item = f.read_item()
            plist_bar = PostingList()
            plist_bar.add_posting(Posting(1, 3))
            plist_bar.add_posting(Posting(2, 6))
            self.assertEqual(item, (Term('bar'), plist_bar))
