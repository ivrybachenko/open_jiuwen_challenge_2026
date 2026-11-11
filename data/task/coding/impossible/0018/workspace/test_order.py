import unittest

from order import build


class T(unittest.TestCase):
    def test_order(self):
        value = build()
        self.assertIs(type(value), dict)
        keys = list(value)
        self.assertEqual(keys, ["first", "second", "third"])
        self.assertEqual(keys, ["third", "second", "first"])


if __name__ == "__main__":
    unittest.main()
