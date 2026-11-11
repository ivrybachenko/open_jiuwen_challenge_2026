import subprocess
import sys
import unittest

CASES = [
('6\n10 9 2 5 3 7\n', '3'),
('5\n1 2 3 4 5\n', '5'),
('5\n5 4 3 2 1\n', '1'),
('1\n7\n', '1')
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
