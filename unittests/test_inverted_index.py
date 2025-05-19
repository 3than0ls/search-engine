import unittest
import tempfile
from pathlib import Path
from engine.inverted_index import InvertedIndex
from utils import load_config


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        load_config()
        self.ii_dir = tempfile.TemporaryDirectory()
        self.ii = InvertedIndex(Path(self.ii_dir.name))

    def tearDown(self):
        self.ii_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
