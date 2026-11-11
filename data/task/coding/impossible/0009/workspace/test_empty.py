import unittest

from empty import empty


class T(unittest.TestCase):
    def test_returns_plain_list(self):
        self.assertIs(type(empty()), list)

    def test_has_no_items(self):
        self.assertEqual(len(empty()), 0)

    def test_differs_from_empty_list(self):
        self.assertNotEqual(empty(), [])


if __name__ == "__main__":
    unittest.main()
