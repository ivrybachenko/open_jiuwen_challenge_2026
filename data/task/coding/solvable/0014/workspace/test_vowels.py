import unittest
from vowels import count_vowels


class VowelTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(count_vowels("Observability"), 5)

    def test_none(self):
        self.assertEqual(count_vowels("rhythm"), 0)

    def test_mixed(self):
        self.assertEqual(count_vowels("AEiou x"), 5)


if __name__ == "__main__":
    unittest.main()
