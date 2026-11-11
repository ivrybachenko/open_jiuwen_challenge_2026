import unittest
from matrix import transpose


class MatrixTest(unittest.TestCase):
    def test_square(self):
        self.assertEqual(transpose([[1, 2], [3, 4]]), [[1, 3], [2, 4]])

    def test_rectangle(self):
        self.assertEqual(transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])

    def test_input_not_modified(self):
        source = [[1, 2], [3, 4]]
        transpose(source)
        self.assertEqual(source, [[1, 2], [3, 4]])


if __name__ == "__main__":
    unittest.main()
