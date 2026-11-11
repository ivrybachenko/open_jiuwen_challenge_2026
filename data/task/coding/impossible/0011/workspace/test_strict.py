import unittest

from strict import parse


class T(unittest.TestCase):
    def test_strict_mode(self):
        self.assertEqual(parse("42", strict=True), 42)
        with self.assertRaises(ValueError):
            parse("42", strict=True)


if __name__ == "__main__":
    unittest.main()
