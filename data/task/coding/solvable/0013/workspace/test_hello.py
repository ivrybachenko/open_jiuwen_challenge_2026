import subprocess
import sys
import unittest


class HelloTest(unittest.TestCase):
    def run_hello(self, *args):
        return subprocess.run(
            [sys.executable, "hello.py", *args],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_named(self):
        completed = self.run_hello("Ada")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "Hello, Ada!\n")

    def test_default(self):
        completed = self.run_hello()
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "Hello, world!\n")


if __name__ == "__main__":
    unittest.main()
