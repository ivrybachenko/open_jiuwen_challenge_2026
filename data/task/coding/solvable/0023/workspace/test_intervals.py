import unittest
from intervals import merge_intervals


class IntervalTest(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(
            merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]),
            [[1, 6], [8, 10], [15, 18]],
        )

    def test_touching(self):
        self.assertEqual(merge_intervals([[1, 2], [2, 5]]), [[1, 5]])

    def test_unsorted(self):
        self.assertEqual(merge_intervals([[5, 6], [1, 2]]), [[1, 2], [5, 6]])


if __name__ == "__main__":
    unittest.main()
