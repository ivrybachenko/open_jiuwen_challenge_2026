import subprocess
import sys
import unittest

CASES = [
('3\n1 3 5\n3 5 6\n6 8 4\n', '15'),
('4\n1 2 3\n2 3 4\n3 4 5\n4 5 6\n', '18'),
('1\n5 5 9\n', '9')
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
