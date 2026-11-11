import unittest

from division import find


class T(unittest.TestCase):
    def test_value(self):
        value = find()
        self.assertIs(type(value), int)
        self.assertEqual(value // 2, 3)
        self.assertEqual(value % 2, 2)


if __name__ == "__main__":
    unittest.main()
