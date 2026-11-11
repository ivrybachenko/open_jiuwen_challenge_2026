import subprocess
import sys
import unittest


class JsonQueryTest(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, "json_query.py", *args],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_nested(self):
        completed = self.run_tool("data.json", "a.b.0.c")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.strip(), "7")

    def test_string(self):
        completed = self.run_tool("data.json", "name")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.strip(), '"demo"')

    def test_missing(self):
        completed = self.run_tool("data.json", "a.missing")
        self.assertEqual(completed.returncode, 1)


if __name__ == "__main__":
    unittest.main()
