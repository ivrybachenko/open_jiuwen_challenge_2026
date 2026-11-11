import subprocess
import sys
import unittest

CASES = [
('1\n', '1'),
('4\n', '2'),
('8\n', '92'),
('10\n', '724')
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
