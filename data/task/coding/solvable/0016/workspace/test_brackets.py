import unittest
from brackets import balanced


class BracketTest(unittest.TestCase):
    def test_valid(self):
        for text in ("", "()", "([{}])", "a(b[c]{d})"):
            self.assertTrue(balanced(text), text)

    def test_invalid(self):
        for text in ("(", "([)]", "}{", "(()"):
            self.assertFalse(balanced(text), text)


if __name__ == "__main__":
    unittest.main()
