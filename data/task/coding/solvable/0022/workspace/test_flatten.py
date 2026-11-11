import unittest
from flatten import flatten


class FlattenTest(unittest.TestCase):
    def test_nested(self):
        self.assertEqual(flatten([1, [2, (3, 4)], 5]), [1, 2, 3, 4, 5])

    def test_empty(self):
        self.assertEqual(flatten([]), [])

    def test_string_leaf(self):
        self.assertEqual(flatten(["ab", ["cd"]]), ["ab", "cd"])


if __name__ == "__main__":
    unittest.main()
