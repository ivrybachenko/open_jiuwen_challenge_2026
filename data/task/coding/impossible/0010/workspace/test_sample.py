import unittest

from sample import sample


class T(unittest.TestCase):
    def test_returns_plain_list(self):
        self.assertIs(type(sample()), list)

    def test_length(self):
        self.assertEqual(len(sample()), 2)

    def test_contents(self):
        self.assertEqual(sorted(sample()), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
