import unittest
from caesar import shift


class CaesarTest(unittest.TestCase):
    def test_forward(self):
        self.assertEqual(shift("abc XYZ", 2), "cde ZAB")

    def test_wrap_backwards(self):
        self.assertEqual(shift("Ada", -1), "Zcz")

    def test_other_characters(self):
        self.assertEqual(shift("a1!b", 3), "d1!e")


if __name__ == "__main__":
    unittest.main()
