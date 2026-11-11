import subprocess
import sys
import unittest

CASES = [
('3 2\n0 1 4\n1 2 5\n0 2\n', '9'),
('4 2\n0 1 3\n2 3 1\n0 3\n', '-1'),
('2 1\n0 1 7\n0 0\n', '0')
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
