import unittest
import tempfile
from pathlib import Path
from index.inverted_index import InvertedIndex
from index.posting import Posting
from utils import load_config


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.ii = InvertedIndex(self.ii_dir.name)

    def tearDown(self):
        self.ii_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
