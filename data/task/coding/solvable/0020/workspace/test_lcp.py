import unittest
from lcp import longest_common_prefix


class PrefixTest(unittest.TestCase):
    def test_common(self):
        self.assertEqual(longest_common_prefix(["flower", "flow", "flight"]), "fl")

    def test_none(self):
        self.assertEqual(longest_common_prefix(["dog", "cat"]), "")

    def test_single_and_empty(self):
        self.assertEqual(longest_common_prefix(["agent"]), "agent")
        self.assertEqual(longest_common_prefix([]), "")


if __name__ == "__main__":
    unittest.main()
