import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CMD = [sys.executable, os.path.join(HERE, "wordfreq.py")]


def run(args, stdin=None):
    return subprocess.run(
        CMD + args,
        cwd=HERE,
        capture_output=True,
        text=True,
        input=stdin,
    )


class T(unittest.TestCase):
    def test_default_top3(self):
        result = run(["sample.txt"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().splitlines(), ["the 4", "dog 2", "fox 2"])

    def test_top_option(self):
        result = run(["sample.txt", "--top", "2"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().splitlines(), ["the 4", "dog 2"])

    def test_min_length(self):
        result = run(["sample.txt", "--min-length", "5", "--top", "3"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().splitlines(), ["barks 1", "brown 1", "jumps 1"])

    def test_stdin_and_punctuation(self):
        result = run(["-"], stdin="Dog, dog. Cat\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().splitlines(), ["dog 2", "cat 1"])

    def test_missing_file(self):
        result = run(["nope.txt"])
        self.assertEqual(result.returncode, 1)

    def test_unknown_option(self):
        result = run(["sample.txt", "--bogus"])
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
