import unittest

from normalize import normalize


class T(unittest.TestCase):
    def test_empty_is_empty(self):
        self.assertEqual(normalize(""), "")

    def test_empty_is_default(self):
        self.assertEqual(normalize(""), "default")

    def test_lowercase(self):
        self.assertEqual(normalize("Hello"), "hello")


if __name__ == "__main__":
    unittest.main()
