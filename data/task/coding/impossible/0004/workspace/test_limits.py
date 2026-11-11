import unittest

from limits import smallest_positive


class T(unittest.TestCase):
    def test_is_integer(self):
        self.assertIs(type(smallest_positive()), int)

    def test_is_positive(self):
        self.assertGreater(smallest_positive(), 0)

    def test_is_below_one(self):
        self.assertLess(smallest_positive(), 1)

    def test_is_stable(self):
        self.assertEqual(smallest_positive(), smallest_positive())


if __name__ == "__main__":
    unittest.main()
