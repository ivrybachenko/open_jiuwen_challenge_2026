import unittest

from schedule import plan


class T(unittest.TestCase):
    def test_plan(self):
        jobs = plan()
        self.assertIs(type(jobs), list)
        self.assertEqual(len(jobs), 3)
        for job in jobs:
            self.assertIs(type(job), tuple)
            self.assertEqual(len(job), 2)
            start, end = job
            self.assertIs(type(start), int)
            self.assertIs(type(end), int)
            self.assertLess(start, end)

        ordered = sorted(jobs)
        for left, right in zip(ordered, ordered[1:]):
            self.assertGreaterEqual(right[0], left[1])

        span = max(end for _, end in jobs) - min(start for start, _ in jobs)
        longest = max(end - start for start, end in jobs)
        self.assertEqual(span, longest)


if __name__ == "__main__":
    unittest.main()
