import unittest
from search import binary_search


class SearchTest(unittest.TestCase):
    def test_found(self):
        values = [1, 3, 5, 7, 9]
        for target in values:
            self.assertEqual(binary_search(values, target), values.index(target))

    def test_missing(self):
        self.assertEqual(binary_search([2, 4, 6], 5), -1)

    def test_empty(self):
        self.assertEqual(binary_search([], 1), -1)


if __name__ == "__main__":
    unittest.main()
