import unittest

from tokens import token


class T(unittest.TestCase):
    def test_identity(self):
        first = token()
        second = token()
        self.assertIs(first, second)
        self.assertIsNot(first, second)


if __name__ == "__main__":
    unittest.main()
