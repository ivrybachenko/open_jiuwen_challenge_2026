import subprocess
import sys
import unittest


class TopProductsTest(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, "top_products.py", *args],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_default_top(self):
        completed = self.run_tool("orders.csv")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "bag 10\nbook 10\npen 10\n")

    def test_explicit_top(self):
        completed = self.run_tool("orders.csv", "--top", "2")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "bag 10\nbook 10\n")


if __name__ == "__main__":
    unittest.main()
