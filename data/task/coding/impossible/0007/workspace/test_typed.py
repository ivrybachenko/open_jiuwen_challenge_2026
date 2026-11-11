import unittest

from typed import identify


class T(unittest.TestCase):
    def test_returns_integer(self):
        self.assertIs(type(identify()), int)

    def test_returns_string(self):
        self.assertIs(type(identify()), str)


if __name__ == "__main__":
    unittest.main()
