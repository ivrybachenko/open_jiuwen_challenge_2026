import unittest
from rle import encode, decode


class RunLengthTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(encode("aaabbc"), "a3b2c1")
        self.assertEqual(encode(""), "")

    def test_decode(self):
        self.assertEqual(decode("a3b2c1"), "aaabbc")
        self.assertEqual(decode(""), "")

    def test_round_trip(self):
        self.assertEqual(decode(encode("zzzzzz")), "zzzzzz")


if __name__ == "__main__":
    unittest.main()
