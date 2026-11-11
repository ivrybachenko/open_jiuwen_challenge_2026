import unittest
from pathlib import Path


class ReadmeTest(unittest.TestCase):
    def test_content(self):
        self.assertEqual(Path("readme.txt").read_text(encoding="utf-8"), "42\n")


if __name__ == "__main__":
    unittest.main()
