import unittest

from counter import next_value


class T(unittest.TestCase):
    def test_same_input_same_output(self):
        self.assertEqual(next_value(7), next_value(7))

    def test_same_input_different_output(self):
        self.assertNotEqual(next_value(7), next_value(7))

    def test_returns_int(self):
        self.assertIsInstance(next_value(7), int)


if __name__ == "__main__":
    unittest.main()
