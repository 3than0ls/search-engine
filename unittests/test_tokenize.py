import unittest
from utils import get_tokens


class TestTokenize(unittest.TestCase):
    def test_get_words(self):
        words = get_tokens("one two two hello world qwerty uiop a 1")
        self.assertEqual(words['one'], 1)
        self.assertEqual(words['two'], 2)
        self.assertEqual(words['hello'], 1)
        self.assertEqual(words['world'], 1)
        self.assertEqual(words['qwerty'], 1)
        self.assertEqual(words['a'], 1)
        self.assertEqual(words['1'], 1)


if __name__ == '__main__':
    unittest.main()
