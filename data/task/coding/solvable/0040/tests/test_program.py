import subprocess
import sys
import unittest

CASES = [
('2 + 3 * 4\n', '14'),
('(2 + 3) * 4\n', '20'),
('100 - 20 - 5\n', '75'),
('2 * (3 + (4 - 1)) * 5\n', '60')
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
