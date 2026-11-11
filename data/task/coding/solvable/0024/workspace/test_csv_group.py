import subprocess
import sys
import unittest


class CsvGroupTest(unittest.TestCase):
    def test_group(self):
        completed = subprocess.run(
            [sys.executable, "csv_group.py", "sales.csv", "region", "units"],
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "North 12\nSouth 2\n")


if __name__ == "__main__":
    unittest.main()
