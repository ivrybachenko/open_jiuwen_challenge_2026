import unittest

from matrix import grid


class T(unittest.TestCase):
    def test_matrix(self):
        values = grid()
        self.assertIs(type(values), list)
        self.assertEqual(len(values), 3)
        for row in values:
            self.assertIs(type(row), list)
            self.assertEqual(len(row), 3)
            for value in row:
                self.assertIs(type(value), int)

        for row in values:
            self.assertEqual(sum(row), 0)

        for column in range(3):
            self.assertEqual(sum(values[row][column] for row in range(3)), 1)


if __name__ == "__main__":
    unittest.main()
