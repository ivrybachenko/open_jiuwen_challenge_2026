import subprocess
import sys
import unittest

CASES = [
('abc\nab?\n', 'YES'),
('abc\nab\n', 'NO'),
('abc\n*\n', 'YES'),
('acccb\na*b\n', 'YES'),
('abcb\n*?*b\n', 'YES')
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
