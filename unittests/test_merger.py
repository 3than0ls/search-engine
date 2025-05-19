import unittest

from index.partial_index.partial_index_merger import PartialIndexMerger
from index.partial_index.partial_index import PartialIndex
from index.posting import Posting
from index.posting_list import PostingList
from index.term import Term
from index.indexer import Indexer
from pathlib import Path
import tempfile
from utils import load_config


class TestMerger(unittest.TestCase):
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

    def test_merge_postings_lists(self):
        self.construct_pi()
        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        left = PostingList()
        right = PostingList()
        left_postings = [Posting(1, 1), Posting(3, 2), Posting(5, 3)]
        right_postings = [Posting(2, 2), Posting(
            4, 3), Posting(6, 4), Posting(8, 5)]
        for posting in left_postings:
            left.add_posting(posting)
        for posting in right_postings:
            right.add_posting(posting)
        merged = merger._merge_postings_lists(left, right)
        self.assertEqual(merged._postings, sorted(
            left_postings + right_postings))

    def test_merge_postings_list2(self):
        self.construct_pi()
        left_term1 = [Posting(1, 1), Posting(3, 2), Posting(5, 3)]
        right_term1 = [Posting(2, 2), Posting(
            4, 3), Posting(6, 4), Posting(8, 5)]

        left_pl = PostingList()
        right_pl = PostingList()

        for term in left_term1:
            left_pl.add_posting(term)
        for term in right_term1:
            right_pl.add_posting(term)

        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        merged = merger._merge_postings_lists(left_pl, right_pl)
        self.assertEqual(merged._postings, sorted(
            left_term1 + right_term1))

        other = PostingList()
        other.add_posting(Posting(100, 100))
        merged = merger._merge_postings_lists(merged, other)
        self.assertEqual(merged._postings, sorted(
            left_term1 + right_term1 + [Posting(100, 100)]))

    def test_merge_postings_list_assertes(self):
        self.construct_pi()
        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        left = PostingList()
        right = PostingList()
        left.add_posting(Posting(1, 1))
        right.add_posting(Posting(1, 1))
        with self.assertRaises(AssertionError):
            merger._merge_postings_lists(left, right)

    def test_merge_uneven_partial_indexes(self):
        # construct partial indexes and serialize
        pi_left = PartialIndex()
        pi_right = PartialIndex()
        pi_all = PartialIndex()
        left_postings = {
            "term1": [Posting(100, 1)],
        }
        right_postings = {
            "term1": [Posting(i, i) for i in range(10)],
            "term2": [Posting(i, i) for i in range(10)],
            "term3": [Posting(i, i) for i in range(10)],
            "term4": [Posting(i, i) for i in range(10)],
        }

        for key, posting_list in left_postings.items():
            for posting in posting_list:
                pi_left.add_posting(Term(key), posting)
                pi_all.add_posting(Term(key), posting)
        for key, posting_list in right_postings.items():
            for posting in posting_list:
                pi_right.add_posting(Term(key), posting)
                pi_all.add_posting(Term(key), posting)

        with open(Path(self.pi_dir.name) / 'partial_index_001.bin', 'wb') as f1, open(Path(self.pi_dir.name) / 'partial_index_002.bin', 'wb') as f2:
            f1.write(pi_left.serialize())
            f2.write(pi_right.serialize())

        with open(Path(self.pi_dir.name) / 'partial_index_001.bin', 'rb') as f1, open(Path(self.pi_dir.name) / 'partial_index_002.bin', 'rb') as f2:
            self.assertEqual(PartialIndex.deserialize(f1.read()), pi_left)
            self.assertEqual(PartialIndex.deserialize(f2.read()), pi_right)

        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        merger._merge_partial_indexes(
            Path(self.pi_dir.name) / 'out.bin',
            Path(self.pi_dir.name) / 'partial_index_001.bin',
            Path(self.pi_dir.name) / 'partial_index_002.bin')

        with open(Path(self.pi_dir.name) / 'out.bin', 'rb') as f:
            out_index = PartialIndex.deserialize(f.read())
            self.assertEqual(out_index, pi_all)

    def test_merge_partial_indexes(self):
        # construct partial indexes and serialize
        pi_left = PartialIndex()
        pi_right = PartialIndex()
        pi_all = PartialIndex()
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
                pi_left.add_posting(Term(key), posting)
                pi_all.add_posting(Term(key), posting)
        for key, posting_list in right_postings.items():
            for posting in posting_list:
                pi_right.add_posting(Term(key), posting)
                pi_all.add_posting(Term(key), posting)

        with open(Path(self.pi_dir.name) / 'partial_index_001.bin', 'wb') as f1, open(Path(self.pi_dir.name) / 'partial_index_002.bin', 'wb') as f2:
            f1.write(pi_left.serialize())
            f2.write(pi_right.serialize())

        with open(Path(self.pi_dir.name) / 'partial_index_001.bin', 'rb') as f1, open(Path(self.pi_dir.name) / 'partial_index_002.bin', 'rb') as f2:
            self.assertEqual(PartialIndex.deserialize(f1.read()), pi_left)
            self.assertEqual(PartialIndex.deserialize(f2.read()), pi_right)

        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        merger._merge_partial_indexes(
            Path(self.pi_dir.name) / 'out.bin',
            Path(self.pi_dir.name) / 'partial_index_001.bin',
            Path(self.pi_dir.name) / 'partial_index_002.bin')

        with open(Path(self.pi_dir.name) / 'out.bin', 'rb') as f:
            out_index = PartialIndex.deserialize(f.read())
            self.assertEqual(out_index, pi_all)

    def test_polyphase_merge(self):
        # construct partial indexes and serialize
        partial_indexes_data = [
            {
                "term1": [Posting(1, 1), Posting(3, 2), Posting(5, 3)],
                "term2": [Posting(201, 201)]
            }, {
                "term1": [Posting(2, 2), Posting(4, 3), Posting(6, 4), Posting(8, 5)],
                "term3": [Posting(302, 302)]
            },
            {
                "term4": [Posting(1, 1), Posting(3, 2), Posting(5, 3)],
                "term5": [Posting(100, 100)]
            }, {
                "term1": [Posting(103, 103), Posting(113, 113)],
                "term3": [Posting(303, 303)],
                "term5": [Posting(503, 503)]
            },
            {
                "term1": [Posting(124, 124)],
                "term2": [Posting(124, 124)],
                "term3": [Posting(124, 124)],
                "term4": [Posting(124, 124)],
                "term5": [Posting(124, 124)]
            },
            {
                "term6": [Posting(i, i) for i in range(1000)],
            },
            {
                "term6": [Posting(i, i) for i in range(1000, 2000)],
            },
            {
                "term1": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)],
                "term2": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)],
                "term3": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)],
                "term4": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)],
                "term5": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)]
            },
            {
                "term1": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)],
                "term2": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)],
                "term3": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)],
                "term4": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)],
                "term5": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)]
            },
            {
                f"term{7+i}": [Posting(1000 + i, 1000 + i) for i in range(0, 50, 2)]
                for i in range(25)
            },
            {
                f"term{7+i}": [Posting(1000 + i, 1000 + i) for i in range(1, 50, 2)]
                for i in range(25)
            }
        ]
        partial_indexes = [PartialIndex()
                           for _ in range(len(partial_indexes_data))]
        pi = PartialIndex()
        num_postings = 0
        for i, data in enumerate(partial_indexes_data):
            for term, posting_list in data.items():
                for posting in posting_list:
                    partial_indexes[i].add_posting(Term(term), posting)
                    pi.add_posting(Term(term), posting)
                    num_postings += 1
            # file name doesn't matter as long as it's in pi_dir for merger
            with open(Path(self.pi_dir.name) / f'partial_index_{i}.bin', 'wb') as f:
                f.write(partial_indexes[i].serialize())
            with open(Path(self.pi_dir.name) / f'partial_index_{i}.bin', 'rb') as f:
                self.assertEqual(PartialIndex.deserialize(
                    f.read()), partial_indexes[i])
        self.assertEqual(num_postings, pi.num_postings())

        merger = PartialIndexMerger(
            Path(self.pi_dir.name), Path(self.ii_dir.name))
        merger.merge()

        with open(Path(self.ii_dir.name) / 'inverted_index.bin', 'rb') as f:
            out_index = PartialIndex.deserialize(f.read())
            self.assertEqual(out_index.num_postings(), pi.num_postings())
            self.assertEqual(out_index, pi)
