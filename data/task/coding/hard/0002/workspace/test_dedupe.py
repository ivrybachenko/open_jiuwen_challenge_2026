import time
import unittest

import dedupe


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(dedupe.first_repeat_index([5, 1, 5, 2]), 2)

    def test_no_repeat(self):
        self.assertEqual(dedupe.first_repeat_index([1, 2, 3]), -1)

    def test_first_of_several(self):
        self.assertEqual(dedupe.first_repeat_index([1, 2, 1, 2, 1]), 2)

    def test_empty(self):
        self.assertEqual(dedupe.first_repeat_index([]), -1)

    def test_performance(self):
        values = list(range(15000))
        started = time.perf_counter()
        result = dedupe.first_repeat_index(values)
        elapsed = time.perf_counter() - started
        self.assertEqual(result, -1)
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
