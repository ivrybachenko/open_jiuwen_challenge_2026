import unittest
from stats import mean, median


class StatsTest(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([2, 4, 6]), 4)
        self.assertAlmostEqual(mean([1, 2]), 1.5)

    def test_median_odd(self):
        self.assertEqual(median([9, 1, 5]), 5)

    def test_median_even(self):
        self.assertEqual(median([4, 1, 3, 2]), 2.5)


if __name__ == "__main__":
    unittest.main()
