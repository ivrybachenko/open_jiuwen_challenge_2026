import unittest

from registry import build


class T(unittest.TestCase):
    def test_returns_plain_dict(self):
        self.assertIs(type(build()), dict)

    def test_two_entries(self):
        self.assertEqual(len(build()), 2)

    def test_integer_key(self):
        self.assertEqual(build()[1], "integer")

    def test_boolean_key(self):
        self.assertEqual(build()[True], "boolean")


if __name__ == "__main__":
    unittest.main()
