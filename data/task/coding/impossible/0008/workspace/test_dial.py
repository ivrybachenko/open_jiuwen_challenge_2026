import unittest

from dial import advance


class T(unittest.TestCase):
    def test_is_integer(self):
        self.assertIs(type(advance()), int)

    def test_one_step_ahead(self):
        value = advance()
        self.assertEqual(value, value + 1)


if __name__ == "__main__":
    unittest.main()
