import unittest

import first
import second


class T(unittest.TestCase):
    def test_values_are_integers(self):
        self.assertIs(type(first.VALUE), int)
        self.assertIs(type(second.VALUE), int)

    def test_second_is_one_more(self):
        self.assertEqual(second.VALUE, first.VALUE + 1)

    def test_first_is_one_more(self):
        self.assertEqual(first.VALUE, second.VALUE + 1)


if __name__ == "__main__":
    unittest.main()
