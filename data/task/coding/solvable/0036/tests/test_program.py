import subprocess
import sys
import unittest

CASES = [
('3 2\n0 1\n1 2\n', '0 1 2'),
('3 3\n0 1\n1 2\n2 0\n', '-1'),
('4 2\n0 2\n1 2\n', '0 1 2 3')
]


class ProgramTest(unittest.TestCase):
    def test_cases(self):
        for stdin_text, expected in CASES:
            with self.subTest(stdin=stdin_text):
                completed = subprocess.run(
                    [sys.executable, "program.py"],
                    input=stdin_text,
                    text=True,
                    capture_output=True,
                    timeout=15,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stdout.strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
