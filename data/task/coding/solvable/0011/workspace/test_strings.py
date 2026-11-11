import unittest
from strings import reverse_text


class ReverseTest(unittest.TestCase):
    def test_words(self):
        self.assertEqual(reverse_text("agent"), "tnega")

    def test_empty(self):
        self.assertEqual(reverse_text(""), "")

    def test_unicode(self):
        self.assertEqual(reverse_text("ab1"), "1ba")


if __name__ == "__main__":
    unittest.main()
