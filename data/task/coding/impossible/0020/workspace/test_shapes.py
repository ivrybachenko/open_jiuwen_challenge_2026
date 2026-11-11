import os
import tempfile
import unittest

from shapes import setup


class T(unittest.TestCase):
    def test_file_and_directory(self):
        with tempfile.TemporaryDirectory() as base:
            path = os.path.join(base, "node")
            setup(path)
            self.assertTrue(os.path.isfile(path))
            self.assertTrue(os.path.isdir(path))


if __name__ == "__main__":
    unittest.main()
