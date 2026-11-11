import unittest

from packer import encode

INPUTS = ["alpha", "beta", "gamma"]
OUTPUTS = {"odd", "even"}


class T(unittest.TestCase):
    def test_outputs_are_labels(self):
        for value in INPUTS:
            self.assertIn(encode(value), OUTPUTS)

    def test_codes_are_strings(self):
        for value in INPUTS:
            self.assertIs(type(encode(value)), str)

    def test_codes_are_distinct(self):
        codes = [encode(value) for value in INPUTS]
        self.assertEqual(len(set(codes)), 3)


if __name__ == "__main__":
    unittest.main()
