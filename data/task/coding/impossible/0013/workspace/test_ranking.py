import unittest

from ranking import ranked


class T(unittest.TestCase):
    def test_ranking(self):
        values = ranked()
        self.assertIs(type(values), list)
        self.assertGreaterEqual(len(values), 3)
        self.assertTrue(all(type(value) is int for value in values))
        self.assertEqual(len(set(values)), len(values))
        self.assertEqual(values, sorted(values))
        self.assertEqual(values, sorted(values, reverse=True))


if __name__ == "__main__":
    unittest.main()
