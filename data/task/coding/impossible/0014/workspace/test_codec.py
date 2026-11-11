import unittest

from codec import encode

ALPHABET = {"A", "B"}


class T(unittest.TestCase):
    def test_codes(self):
        codes = [encode(number) for number in range(1000)]
        for code in codes:
            self.assertIs(type(code), str)
            self.assertLessEqual(len(code), 2)
            self.assertTrue(set(code) <= ALPHABET)
        self.assertEqual(len(set(codes)), 1000)


if __name__ == "__main__":
    unittest.main()
