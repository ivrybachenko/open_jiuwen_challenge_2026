import unittest
from parity import is_even


class ParityTest(unittest.TestCase):
    def test_even(self):
        for value in (0, 2, 4, -6, 100):
            self.assertTrue(is_even(value), value)

    def test_odd(self):
        for value in (1, 3, -1, -7, 99):
            self.assertFalse(is_even(value), value)


if __name__ == "__main__":
    unittest.main()
