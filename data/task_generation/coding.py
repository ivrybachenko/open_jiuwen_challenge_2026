"""Generate the 34 new coding tasks (``coding/solvable/0007``..``0040``)."""

from __future__ import annotations

from common import create_task


def _visible(index: int, task_id: str, instruction: str, reward: int,
             files: dict[str, str], reference: dict[str, str]) -> None:
    create_task(
        category="coding",
        index=index,
        task_id=task_id,
        instruction=instruction,
        reward=reward,
        check="unittest",
        expected="tests_pass",
        workspace=files,
        reference=reference,
    )


def _hidden(index: int, task_id: str, instruction: str, reward: int,
            starter: str, reference: str, cases: list[tuple[str, str]]) -> None:
    case_lines = ",\n".join(repr(case) for case in cases)
    test = f'''import subprocess
import sys
import unittest

CASES = [
{case_lines}
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
'''
    create_task(
        category="coding",
        index=index,
        task_id=task_id,
        instruction=instruction,
        reward=reward,
        check="hidden_unittest",
        expected="tests_pass",
        workspace={"program.py": starter},
        hidden_tests={"tests/test_program.py": test},
        reference={"program.py": reference},
    )


def generate() -> None:
    # Very small tasks: file creation and a tiny refactor.
    create_task(
        category="coding", index=7, task_id="coding_0201",
        instruction=(
            "Create a file named readme.txt in the current directory. Its entire "
            "content must be the number 42 followed by one newline. Then write "
            "ONLY the final answer to the file answer.txt in the current "
            "directory (for example with bash: echo 42 > answer.txt)."
        ),
        reward=3, check="hidden_unittest", expected="tests_pass",
        hidden_tests={
            "tests/test_readme.py": '''import unittest
from pathlib import Path


class ReadmeTest(unittest.TestCase):
    def test_content(self):
        self.assertEqual(Path("readme.txt").read_text(encoding="utf-8"), "42\\n")


if __name__ == "__main__":
    unittest.main()
''',
        },
        reference={"readme.txt": "42\n"},
    )
    create_task(
        category="coding", index=8, task_id="coding_0202",
        instruction=(
            "The file run.sh contains a short shell program. Make it executable "
            "and run it. Write what it prints, with the trailing newline "
            "removed, to answer.txt in the current directory."
        ),
        reward=2, check="exact_str", expected="HELLO-42",
        workspace={"run.sh": "#!/bin/sh\nprintf 'HELLO-42\\n'\n"},
    )

    _visible(
        9, "coding_0203",
        "Implement is_even(n) in parity.py. It must return True for even "
        "integers and False otherwise, including negative numbers. Run "
        "`python3 test_parity.py`; do not edit the tests. Work only inside the "
        "current directory. When you are done, write ONLY the word DONE to the "
        "file answer.txt in the current directory.",
        1,
        {
            "parity.py": "def is_even(n):\n    return n % 2 == 1\n",
            "test_parity.py": '''import unittest
from parity import is_even


class ParityTest(unittest.TestCase):
    def test_even(self):
        for value in (0, 2, 4, -6, 100):
            self.assertTrue(is_even(value), value)

    def test_odd(self):
        for value in (1, 3, -1, -7, 99):
            self.assertFalse(is_even(value), value)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {"parity.py": "def is_even(n):\n    return n % 2 == 0\n"},
    )

    _visible(
        10, "coding_0204",
        "The module greeting.py does not even import because of a syntax error. "
        "Fix it so that greet(name) returns 'Hello, <name>!'. Run "
        "`python3 test_greeting.py`; do not edit the tests. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "the file answer.txt in the current directory.",
        2,
        {
            "greeting.py": 'def greet(name)\n    return "Hello, " + name + "!"\n',
            "test_greeting.py": '''import unittest
from greeting import greet


class GreetingTest(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_empty(self):
        self.assertEqual(greet(""), "Hello, !")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {"greeting.py": 'def greet(name):\n    return "Hello, " + name + "!"\n'},
    )

    _visible(
        11, "coding_0205",
        "Implement reverse_text(text) in strings.py. It must return the "
        "characters of text in reverse order. Run `python3 test_strings.py`; do "
        "not edit the tests. Work only inside the current directory. When you "
        "are done, write ONLY the word DONE to answer.txt.",
        1,
        {
            "strings.py": "def reverse_text(text):\n    return text\n",
            "test_strings.py": '''import unittest
from strings import reverse_text


class ReverseTest(unittest.TestCase):
    def test_words(self):
        self.assertEqual(reverse_text("agent"), "tnega")

    def test_empty(self):
        self.assertEqual(reverse_text(""), "")

    def test_unicode(self):
        self.assertEqual(reverse_text("ab1"), "1ba")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {"strings.py": "def reverse_text(text):\n    return text[::-1]\n"},
    )

    _visible(
        12, "coding_0206",
        "Implement mean(values) and median(values) in stats.py. Each function "
        "receives a non-empty list of numbers. The median of an even-length "
        "list is the average of the two middle values. Run "
        "`python3 test_stats.py`; do not edit the tests. Work only inside the "
        "current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        3,
        {
            "stats.py": "def mean(values):\n    return sum(values)\n\n\ndef median(values):\n    return values[0]\n",
            "test_stats.py": '''import unittest
from stats import mean, median


class StatsTest(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([2, 4, 6]), 4)
        self.assertAlmostEqual(mean([1, 2]), 1.5)

    def test_median_odd(self):
        self.assertEqual(median([9, 1, 5]), 5)

    def test_median_even(self):
        self.assertEqual(median([4, 1, 3, 2]), 2.5)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "stats.py": '''def mean(values):
    return sum(values) / len(values)


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
''',
        },
    )

    _visible(
        13, "coding_0207",
        "Implement the command-line program hello.py. With an argument it must "
        "print 'Hello, <argument>!'; without arguments it must print "
        "'Hello, world!'. Run `python3 test_hello.py`; do not edit the tests. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the word DONE to answer.txt.",
        2,
        {
            "hello.py": "import sys\n\nprint('Hello!')\n",
            "test_hello.py": '''import subprocess
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
        self.assertEqual(completed.stdout, "Hello, Ada!\\n")

    def test_default(self):
        completed = self.run_hello()
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "Hello, world!\\n")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "hello.py": '''import sys

name = sys.argv[1] if len(sys.argv) > 1 else "world"
print(f"Hello, {name}!")
''',
        },
    )

    _visible(
        14, "coding_0208",
        "Implement count_vowels(text) in vowels.py. Count the letters a, e, i, "
        "o, u regardless of case; do not count y. Run `python3 test_vowels.py`; "
        "do not edit the tests. Work only inside the current directory. When "
        "you are done, write ONLY the word DONE to answer.txt.",
        1,
        {
            "vowels.py": "def count_vowels(text):\n    return len(text)\n",
            "test_vowels.py": '''import unittest
from vowels import count_vowels


class VowelTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(count_vowels("Observability"), 5)

    def test_none(self):
        self.assertEqual(count_vowels("rhythm"), 0)

    def test_mixed(self):
        self.assertEqual(count_vowels("AEiou x"), 5)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {"vowels.py": "def count_vowels(text):\n    return sum(1 for ch in text.lower() if ch in 'aeiou')\n"},
    )

    _visible(
        15, "coding_0209",
        "Implement encode(text) and decode(text) for run-length encoding in "
        "rle.py. A run is written as the character followed by its count, for "
        "example 'aaabb' becomes 'a3b2'. Counts are always positive and no "
        "count is omitted. Run `python3 test_rle.py`; do not edit the tests. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the word DONE to answer.txt.",
        4,
        {
            "rle.py": "def encode(text):\n    return text\n\n\ndef decode(text):\n    return text\n",
            "test_rle.py": '''import unittest
from rle import encode, decode


class RunLengthTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(encode("aaabbc"), "a3b2c1")
        self.assertEqual(encode(""), "")

    def test_decode(self):
        self.assertEqual(decode("a3b2c1"), "aaabbc")
        self.assertEqual(decode(""), "")

    def test_round_trip(self):
        self.assertEqual(decode(encode("zzzzzz")), "zzzzzz")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "rle.py": '''def encode(text):
    if not text:
        return ""
    parts = []
    current = text[0]
    count = 1
    for ch in text[1:]:
        if ch == current:
            count += 1
        else:
            parts.append(f"{current}{count}")
            current = ch
            count = 1
    parts.append(f"{current}{count}")
    return "".join(parts)


def decode(text):
    parts = []
    index = 0
    while index < len(text):
        ch = text[index]
        index += 1
        start = index
        while index < len(text) and text[index].isdigit():
            index += 1
        parts.append(ch * int(text[start:index]))
    return "".join(parts)
''',
        },
    )

    _visible(
        16, "coding_0210",
        "Implement balanced(text) in brackets.py. Return True when every "
        "opening bracket has a matching closing bracket of the same kind and "
        "brackets are properly nested. The kinds are (), [] and {}. Ignore all "
        "other characters. Run `python3 test_brackets.py`; do not edit the "
        "tests. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        3,
        {
            "brackets.py": "def balanced(text):\n    return True\n",
            "test_brackets.py": '''import unittest
from brackets import balanced


class BracketTest(unittest.TestCase):
    def test_valid(self):
        for text in ("", "()", "([{}])", "a(b[c]{d})"):
            self.assertTrue(balanced(text), text)

    def test_invalid(self):
        for text in ("(", "([)]", "}{", "(()"):
            self.assertFalse(balanced(text), text)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "brackets.py": '''def balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''',
        },
    )

    _visible(
        17, "coding_0211",
        "Implement shift(text, amount) in caesar.py. Shift ASCII letters by "
        "amount positions, wrapping inside the same case, and leave every "
        "other character unchanged. Run `python3 test_caesar.py`; do not edit "
        "the tests. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        3,
        {
            "caesar.py": "def shift(text, amount):\n    return text\n",
            "test_caesar.py": '''import unittest
from caesar import shift


class CaesarTest(unittest.TestCase):
    def test_forward(self):
        self.assertEqual(shift("abc XYZ", 2), "cde ZAB")

    def test_wrap_backwards(self):
        self.assertEqual(shift("Ada", -1), "Zcz")

    def test_other_characters(self):
        self.assertEqual(shift("a1!b", 3), "d1!e")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "caesar.py": '''def shift(text, amount):
    result = []
    for ch in text:
        if "a" <= ch <= "z":
            result.append(chr((ord(ch) - ord("a") + amount) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            result.append(chr((ord(ch) - ord("A") + amount) % 26 + ord("A")))
        else:
            result.append(ch)
    return "".join(result)
''',
        },
    )

    _visible(
        18, "coding_0212",
        "Implement binary_search(values, target) in search.py. values is sorted "
        "in ascending order. Return any index where target occurs, or -1 when "
        "target is absent. Run `python3 test_search.py`; do not edit the tests. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the word DONE to answer.txt.",
        2,
        {
            "search.py": "def binary_search(values, target):\n    return 0\n",
            "test_search.py": '''import unittest
from search import binary_search


class SearchTest(unittest.TestCase):
    def test_found(self):
        values = [1, 3, 5, 7, 9]
        for target in values:
            self.assertEqual(binary_search(values, target), values.index(target))

    def test_missing(self):
        self.assertEqual(binary_search([2, 4, 6], 5), -1)

    def test_empty(self):
        self.assertEqual(binary_search([], 1), -1)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "search.py": '''def binary_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1
''',
        },
    )

    _visible(
        19, "coding_0213",
        "Implement transpose(matrix) in matrix.py. The input is a rectangular "
        "list of lists. Return a new matrix whose rows are the columns of the "
        "input. Do not modify the input. Run `python3 test_matrix.py`; do not "
        "edit the tests. Work only inside the current directory. When you are "
        "done, write ONLY the word DONE to answer.txt.",
        2,
        {
            "matrix.py": "def transpose(matrix):\n    return matrix\n",
            "test_matrix.py": '''import unittest
from matrix import transpose


class MatrixTest(unittest.TestCase):
    def test_square(self):
        self.assertEqual(transpose([[1, 2], [3, 4]]), [[1, 3], [2, 4]])

    def test_rectangle(self):
        self.assertEqual(transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])

    def test_input_not_modified(self):
        source = [[1, 2], [3, 4]]
        transpose(source)
        self.assertEqual(source, [[1, 2], [3, 4]])


if __name__ == "__main__":
    unittest.main()
''',
        },
        {"matrix.py": "def transpose(matrix):\n    return [list(row) for row in zip(*matrix)]\n"},
    )

    _visible(
        20, "coding_0214",
        "Implement longest_common_prefix(words) in lcp.py. Return the longest "
        "string that is a prefix of every word. Return an empty string when "
        "the list is empty or there is no common prefix. Run "
        "`python3 test_lcp.py`; do not edit the tests. Work only inside the "
        "current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        3,
        {
            "lcp.py": "def longest_common_prefix(words):\n    return words[0] if words else ''\n",
            "test_lcp.py": '''import unittest
from lcp import longest_common_prefix


class PrefixTest(unittest.TestCase):
    def test_common(self):
        self.assertEqual(longest_common_prefix(["flower", "flow", "flight"]), "fl")

    def test_none(self):
        self.assertEqual(longest_common_prefix(["dog", "cat"]), "")

    def test_single_and_empty(self):
        self.assertEqual(longest_common_prefix(["agent"]), "agent")
        self.assertEqual(longest_common_prefix([]), "")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "lcp.py": '''def longest_common_prefix(words):
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
''',
        },
    )

    _visible(
        21, "coding_0215",
        "Implement parse_config(text) in config.py. Every non-empty line is "
        "either a comment starting with '#' or a 'key=value' pair. Surrounding "
        "spaces around keys and values must be removed. A later duplicate key "
        "overrides an earlier one. Return a dict. Run `python3 test_config.py`; "
        "do not edit the tests. Work only inside the current directory. When "
        "you are done, write ONLY the word DONE to answer.txt.",
        4,
        {
            "config.py": "def parse_config(text):\n    return {}\n",
            "test_config.py": '''import unittest
from config import parse_config


TEXT = """
# service settings
host = localhost
port=8080

port = 9090
name = demo service
"""


class ConfigTest(unittest.TestCase):
    def test_values(self):
        self.assertEqual(
            parse_config(TEXT),
            {"host": "localhost", "port": "9090", "name": "demo service"},
        )

    def test_empty_and_comments(self):
        self.assertEqual(parse_config("\\n# only a comment\\n"), {})


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "config.py": '''def parse_config(text):
    result = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result
''',
        },
    )

    _visible(
        22, "coding_0216",
        "Implement flatten(value) in flatten.py. Recursively flatten nested "
        "lists and tuples into one list, preserving order. Strings and other "
        "values are leaves. Run `python3 test_flatten.py`; do not edit the "
        "tests. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        4,
        {
            "flatten.py": "def flatten(value):\n    return list(value)\n",
            "test_flatten.py": '''import unittest
from flatten import flatten


class FlattenTest(unittest.TestCase):
    def test_nested(self):
        self.assertEqual(flatten([1, [2, (3, 4)], 5]), [1, 2, 3, 4, 5])

    def test_empty(self):
        self.assertEqual(flatten([]), [])

    def test_string_leaf(self):
        self.assertEqual(flatten(["ab", ["cd"]]), ["ab", "cd"])


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "flatten.py": '''def flatten(value):
    result = []
    for item in value:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
''',
        },
    )

    _visible(
        23, "coding_0217",
        "Implement merge_intervals(intervals) in intervals.py. Each interval "
        "is a [start, end] pair. Merge every pair that overlaps or touches "
        "another interval and return the result sorted by start. Run "
        "`python3 test_intervals.py`; do not edit the tests. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        5,
        {
            "intervals.py": "def merge_intervals(intervals):\n    return intervals\n",
            "test_intervals.py": '''import unittest
from intervals import merge_intervals


class IntervalTest(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(
            merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]),
            [[1, 6], [8, 10], [15, 18]],
        )

    def test_touching(self):
        self.assertEqual(merge_intervals([[1, 2], [2, 5]]), [[1, 5]])

    def test_unsorted(self):
        self.assertEqual(merge_intervals([[5, 6], [1, 2]]), [[1, 2], [5, 6]])


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "intervals.py": '''def merge_intervals(intervals):
    ordered = sorted(intervals)
    merged = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
''',
        },
    )

    _visible(
        24, "coding_0218",
        "Implement the command-line program csv_group.py. Usage: "
        "`python3 csv_group.py FILE KEY_COLUMN VALUE_COLUMN`. The CSV file has "
        "a header row. Sum VALUE_COLUMN as integers for each value of "
        "KEY_COLUMN and print one line per key, sorted by key, in the form "
        "`key total`. Run `python3 test_csv_group.py`; do not edit the tests. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the word DONE to answer.txt.",
        5,
        {
            "csv_group.py": "import sys\n\nprint('')\n",
            "sales.csv": "region,units\nNorth,5\nSouth,2\nNorth,7\n",
            "test_csv_group.py": '''import subprocess
import sys
import unittest


class CsvGroupTest(unittest.TestCase):
    def test_group(self):
        completed = subprocess.run(
            [sys.executable, "csv_group.py", "sales.csv", "region", "units"],
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "North 12\\nSouth 2\\n")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "csv_group.py": '''import csv
import sys

path, key_column, value_column = sys.argv[1:4]
totals = {}
with open(path, newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        key = row[key_column]
        totals[key] = totals.get(key, 0) + int(row[value_column])
for key in sorted(totals):
    print(key, totals[key])
''',
        },
    )

    _visible(
        25, "coding_0219",
        "Implement the command-line program top_products.py. Usage: "
        "`python3 top_products.py FILE [--top N]`. The CSV file has columns "
        "product,units. Sum units per product and print the N products with "
        "the largest total, one per line as `product total`. Break ties by "
        "product name in ascending order. Default N is 3. Run "
        "`python3 test_top_products.py`; do not edit the tests. Work only "
        "inside the current directory. When you are done, write ONLY the word "
        "DONE to answer.txt.",
        5,
        {
            "top_products.py": "print('')\n",
            "orders.csv": "product,units\npen,4\nbook,10\npen,6\nbag,10\n",
            "test_top_products.py": '''import subprocess
import sys
import unittest


class TopProductsTest(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, "top_products.py", *args],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_default_top(self):
        completed = self.run_tool("orders.csv")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "bag 10\\nbook 10\\npen 10\\n")

    def test_explicit_top(self):
        completed = self.run_tool("orders.csv", "--top", "2")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "bag 10\\nbook 10\\n")


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "top_products.py": '''import csv
import sys

path = sys.argv[1]
top = 3
if "--top" in sys.argv:
    top = int(sys.argv[sys.argv.index("--top") + 1])
totals = {}
with open(path, newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        name = row["product"]
        totals[name] = totals.get(name, 0) + int(row["units"])
ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
for name, total in ordered[:top]:
    print(name, total)
''',
        },
    )

    _visible(
        26, "coding_0220",
        "Implement the class LRUCache in lru.py. The constructor takes a "
        "positive capacity. get(key) returns the stored value or -1. put(key, "
        "value) inserts or updates a key and evicts the least recently used "
        "entry when the capacity is exceeded. Both get and put count as use. "
        "Run `python3 test_lru.py`; do not edit the tests. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        6,
        {
            "lru.py": '''class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity

    def get(self, key):
        return -1

    def put(self, key, value):
        pass
''',
            "test_lru.py": '''import unittest
from lru import LRUCache


class LRUTest(unittest.TestCase):
    def test_eviction(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        self.assertEqual(cache.get(1), 10)
        cache.put(3, 30)
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(3), 30)

    def test_update(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        cache.put(1, 2)
        self.assertEqual(cache.get(1), 2)

    def test_missing(self):
        self.assertEqual(LRUCache(2).get(9), -1)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "lru.py": '''from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = OrderedDict()

    def get(self, key):
        if key not in self.items:
            return -1
        self.items.move_to_end(key)
        return self.items[key]

    def put(self, key, value):
        if key in self.items:
            self.items.move_to_end(key)
        self.items[key] = value
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)
''',
        },
    )

    _visible(
        27, "coding_0221",
        "Implement to_roman(number) and from_roman(text) in roman.py. Support "
        "numbers from 1 to 3999 inclusive. Use standard subtractive notation. "
        "Run `python3 test_roman.py`; do not edit the tests. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        5,
        {
            "roman.py": "def to_roman(number):\n    return ''\n\n\ndef from_roman(text):\n    return 0\n",
            "test_roman.py": '''import unittest
from roman import from_roman, to_roman


class RomanTest(unittest.TestCase):
    def test_to_roman(self):
        cases = {1: "I", 4: "IV", 9: "IX", 58: "LVIII", 1994: "MCMXCIV", 3999: "MMMCMXCIX"}
        for number, text in cases.items():
            self.assertEqual(to_roman(number), text)

    def test_from_roman(self):
        for number, text in {1: "I", 4: "IV", 58: "LVIII", 1994: "MCMXCIV"}.items():
            self.assertEqual(from_roman(text), number)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "roman.py": '''VALUES = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def to_roman(number):
    parts = []
    for value, text in VALUES:
        while number >= value:
            parts.append(text)
            number -= value
    return "".join(parts)


def from_roman(text):
    index = 0
    total = 0
    for value, token in VALUES:
        while text[index:index + len(token)] == token:
            total += value
            index += len(token)
    return total
''',
        },
    )

    _visible(
        28, "coding_0222",
        "Implement parse_date(text) in dates.py. Accept three formats: "
        "YYYY-MM-DD, DD.MM.YYYY and 'Month D, YYYY' where Month is the English "
        "full month name. Return the date in YYYY-MM-DD form. Raise ValueError "
        "for any other input. Run `python3 test_dates.py`; do not edit the "
        "tests. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        6,
        {
            "dates.py": "def parse_date(text):\n    return text\n",
            "test_dates.py": '''import unittest
from dates import parse_date


class DateTest(unittest.TestCase):
    def test_iso(self):
        self.assertEqual(parse_date("2024-02-29"), "2024-02-29")

    def test_dotted(self):
        self.assertEqual(parse_date("05.11.2023"), "2023-11-05")

    def test_long(self):
        self.assertEqual(parse_date("March 7, 2021"), "2021-03-07")

    def test_invalid(self):
        for value in ("2024/01/01", "32.01.2024", "Not a date"):
            with self.assertRaises(ValueError):
                parse_date(value)


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "dates.py": '''import datetime


MONTHS = {
    name: number
    for number, name in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"],
        start=1,
    )
}


def parse_date(text):
    try:
        if len(text) == 10 and text[4] == "-" and text[7] == "-":
            year, month, day = map(int, text.split("-"))
        elif len(text) == 10 and text[2] == "." and text[5] == ".":
            day, month, year = map(int, text.split("."))
        else:
            month_name, day_text, year_text = text.replace(",", "").split()
            month = MONTHS[month_name]
            day = int(day_text)
            year = int(year_text)
        return datetime.date(year, month, day).isoformat()
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"unsupported date: {text!r}") from None
''',
        },
    )

    _visible(
        29, "coding_0223",
        "Implement the command-line program json_query.py. Usage: "
        "`python3 json_query.py FILE PATH`, where PATH is a dot-separated path "
        "such as `a.b.0.c`. Read the JSON value, follow the path (list indexes "
        "are decimal numbers) and print the selected value as compact JSON. "
        "If the path does not exist, exit with code 1. Run "
        "`python3 test_json_query.py`; do not edit the tests. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        6,
        {
            "json_query.py": "import sys\n\nprint('null')\n",
            "data.json": '{"a": {"b": [{"c": 7}, 8]}, "name": "demo"}\n',
            "test_json_query.py": '''import subprocess
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
''',
        },
        {
            "json_query.py": '''import json
import sys

path, query = sys.argv[1:3]
with open(path, encoding="utf-8") as handle:
    value = json.load(handle)
for part in query.split("."):
    try:
        if isinstance(value, list):
            value = value[int(part)]
        else:
            value = value[part]
    except (KeyError, IndexError, TypeError, ValueError):
        sys.exit(1)
print(json.dumps(value, separators=(",", ":"), ensure_ascii=False))
''',
        },
    )

    _visible(
        30, "coding_0224",
        "Implement sort_versions(versions) in semver.py. Every version is a "
        "string with three non-negative integer parts separated by dots. "
        "Return a new list sorted in ascending order by numeric parts, not as "
        "text. Run `python3 test_semver.py`; do not edit the tests. Work only "
        "inside the current directory. When you are done, write ONLY the word "
        "DONE to answer.txt.",
        4,
        {
            "semver.py": "def sort_versions(versions):\n    return sorted(versions)\n",
            "test_semver.py": '''import unittest
from semver import sort_versions


class SemverTest(unittest.TestCase):
    def test_numeric_order(self):
        self.assertEqual(
            sort_versions(["1.10.0", "1.2.0", "1.2.10", "0.9.9"]),
            ["0.9.9", "1.2.0", "1.2.10", "1.10.0"],
        )

    def test_input_not_modified(self):
        source = ["2.0.0", "1.0.0"]
        sort_versions(source)
        self.assertEqual(source, ["2.0.0", "1.0.0"])


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "semver.py": '''def sort_versions(versions):
    return sorted(versions, key=lambda text: tuple(int(part) for part in text.split(".")))
''',
        },
    )

    _visible(
        31, "coding_0225",
        "Implement parse_events(lines) in events.py. Each non-empty line has "
        "the form '<timestamp> <user> <action>'. Return a dict that maps each "
        "user to a dict of action counts. Ignore empty lines. Run "
        "`python3 test_events.py`; do not edit the tests. Work only inside the "
        "current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        5,
        {
            "events.py": "def parse_events(lines):\n    return {}\n",
            "test_events.py": '''import unittest
from events import parse_events


class EventsTest(unittest.TestCase):
    def test_counts(self):
        lines = [
            "10 alice login",
            "11 bob login",
            "12 alice view",
            "13 alice login",
            "",
        ]
        self.assertEqual(
            parse_events(lines),
            {"alice": {"login": 2, "view": 1}, "bob": {"login": 1}},
        )

    def test_empty(self):
        self.assertEqual(parse_events([]), {})


if __name__ == "__main__":
    unittest.main()
''',
        },
        {
            "events.py": '''def parse_events(lines):
    result = {}
    for line in lines:
        if not line.strip():
            continue
        _timestamp, user, action = line.split()
        actions = result.setdefault(user, {})
        actions[action] = actions.get(action, 0) + 1
    return result
''',
        },
    )

    # Algorithmic tasks with tests kept outside the working directory.
    _hidden(
        32, "coding_0226",
        "Write program.py. It reads an undirected weighted graph from standard "
        "input: the first line has n and m, then m lines have u v w (0-based "
        "vertices, positive integer weights), then one line has s and t. Print "
        "the length of the shortest s-to-t path, or -1 if t is unreachable. "
        "Use only the Python standard library. Work only inside the current "
        "directory. When you are done, write ONLY the word DONE to answer.txt.",
        7,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import heapq
import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        graph[u].append((v, w))
        graph[v].append((u, w))
    start = int(next(it))
    target = int(next(it))
    distances = [10**30] * n
    distances[start] = 0
    queue = [(0, start)]
    while queue:
        distance, node = heapq.heappop(queue)
        if distance != distances[node]:
            continue
        for neighbour, weight in graph[node]:
            candidate = distance + weight
            if candidate < distances[neighbour]:
                distances[neighbour] = candidate
                heapq.heappush(queue, (candidate, neighbour))
    print(-1 if distances[target] == 10**30 else distances[target])


if __name__ == "__main__":
    main()
''',
        [
            ("3 2\n0 1 4\n1 2 5\n0 2\n", "9"),
            ("4 2\n0 1 3\n2 3 1\n0 3\n", "-1"),
            ("2 1\n0 1 7\n0 0\n", "0"),
        ],
    )

    _hidden(
        33, "coding_0227",
        "Write program.py. It reads two strings on separate lines and prints "
        "the Levenshtein edit distance between them (insertions, deletions and "
        "substitutions each cost 1). Work only inside the current directory. "
        "When you are done, write ONLY the word DONE to answer.txt.",
        7,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import sys


def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        return
    a, b = lines[0], lines[1]
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            current.append(min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (ca != cb),
            ))
        previous = current
    print(previous[-1])


if __name__ == "__main__":
    main()
''',
        [
            ("kitten\nsitting\n", "3"),
            ("\nabc\n", "3"),
            ("same\nsame\n", "0"),
            ("flaw\nlawn\n", "2"),
        ],
    )

    _hidden(
        34, "coding_0228",
        "Write program.py. The first line contains n and target. The second "
        "line contains n positive coin values. Print the number of ordered "
        "ways to make exactly target, modulo 1000000007. Every coin value may "
        "be used any number of times. Work only inside the current directory. "
        "When you are done, write ONLY the word DONE to answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import sys

MOD = 1000000007


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    target = int(data[1])
    coins = list(map(int, data[2:2 + n]))
    ways = [0] * (target + 1)
    ways[0] = 1
    for amount in range(1, target + 1):
        ways[amount] = sum(ways[amount - coin] for coin in coins if coin <= amount) % MOD
    print(ways[target])


if __name__ == "__main__":
    main()
''',
        [
            ("3 5\n1 2 5\n", "9"),
            ("2 3\n2 3\n", "1"),
            ("1 0\n7\n", "1"),
            ("2 10\n2 4\n", "8"),
        ],
    )

    _hidden(
        35, "coding_0229",
        "Write program.py. It reads n followed by n integers and prints the "
        "length of the longest strictly increasing subsequence. The solution "
        "must handle n up to 200000. Work only inside the current directory. "
        "When you are done, write ONLY the word DONE to answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import bisect
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    n = data[0]
    values = data[1:1 + n]
    tails = []
    for value in values:
        position = bisect.bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    print(len(tails))


if __name__ == "__main__":
    main()
''',
        [
            ("6\n10 9 2 5 3 7\n", "3"),
            ("5\n1 2 3 4 5\n", "5"),
            ("5\n5 4 3 2 1\n", "1"),
            ("1\n7\n", "1"),
        ],
    )

    _hidden(
        36, "coding_0230",
        "Write program.py. It reads n and m, then m directed edges u v. Print "
        "the lexicographically smallest topological order as space-separated "
        "vertices, or -1 if the graph has a cycle. Vertices are numbered from "
        "0 to n-1. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import heapq
import sys


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    n, m = data[0], data[1]
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    position = 2
    for _ in range(m):
        u, v = data[position], data[position + 1]
        position += 2
        graph[u].append(v)
        indegree[v] += 1
    ready = [node for node in range(n) if indegree[node] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                heapq.heappush(ready, neighbour)
    print(" ".join(map(str, order)) if len(order) == n else -1)


if __name__ == "__main__":
    main()
''',
        [
            ("3 2\n0 1\n1 2\n", "0 1 2"),
            ("3 3\n0 1\n1 2\n2 0\n", "-1"),
            ("4 2\n0 2\n1 2\n", "0 1 2 3"),
        ],
    )

    _hidden(
        37, "coding_0231",
        "Write program.py. It reads two lines: a text and a pattern. The "
        "pattern may contain '?' for exactly one character and '*' for any "
        "sequence of characters, including an empty one. Print YES if the "
        "whole text matches the whole pattern, otherwise NO. Work only inside "
        "the current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import sys


def matches(text, pattern):
    previous = [False] * (len(text) + 1)
    previous[0] = True
    for token in pattern:
        current = [False] * (len(text) + 1)
        if token == "*":
            current[0] = previous[0]
            for j in range(1, len(text) + 1):
                current[j] = previous[j] or current[j - 1]
        else:
            for j in range(1, len(text) + 1):
                current[j] = previous[j - 1] and (token == "?" or token == text[j - 1])
        previous = current
    return previous[-1]


def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        return
    print("YES" if matches(lines[0], lines[1]) else "NO")


if __name__ == "__main__":
    main()
''',
        [
            ("abc\nab?\n", "YES"),
            ("abc\nab\n", "NO"),
            ("abc\n*\n", "YES"),
            ("acccb\na*b\n", "YES"),
            ("abcb\n*?*b\n", "YES"),
        ],
    )

    _hidden(
        38, "coding_0232",
        "Write program.py. It reads n, then n lines with start end weight "
        "(inclusive integer days and a positive weight). Choose a set of "
        "non-overlapping intervals to maximise the total weight. Intervals "
        "that touch at an endpoint do not overlap. Print the maximum total. "
        "Work only inside the current directory. When you are done, write "
        "ONLY the word DONE to answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import bisect
import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    jobs = []
    position = 1
    for _ in range(n):
        start = int(data[position])
        end = int(data[position + 1])
        weight = int(data[position + 2])
        position += 3
        jobs.append((end, start, weight))
    jobs.sort()
    ends = [job[0] for job in jobs]
    best = [0] * (n + 1)
    for i, (end, start, weight) in enumerate(jobs, start=1):
        compatible = bisect.bisect_right(ends, start, 0, i - 1)
        best[i] = max(best[i - 1], best[compatible] + weight)
    print(best[n])


if __name__ == "__main__":
    main()
''',
        [
            ("3\n1 3 5\n3 5 6\n6 8 4\n", "15"),
            ("4\n1 2 3\n2 3 4\n3 4 5\n4 5 6\n", "18"),
            ("1\n5 5 9\n", "9"),
        ],
    )

    _hidden(
        39, "coding_0233",
        "Write program.py. It reads an integer n and prints the number of "
        "ways to place n non-attacking queens on an n by n board. For n from "
        "1 to 10 the result fits in a normal integer. Work only inside the "
        "current directory. When you are done, write ONLY the word DONE to "
        "answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import sys


def count(n, row=0, columns=(), diagonals=(), anti=()):
    if row == n:
        return 1
    total = 0
    for column in range(n):
        if column in columns or row - column in diagonals or row + column in anti:
            continue
        total += count(
            n,
            row + 1,
            columns + (column,),
            diagonals + (row - column,),
            anti + (row + column,),
        )
    return total


def main():
    text = sys.stdin.read().strip()
    if text:
        print(count(int(text)))


if __name__ == "__main__":
    main()
''',
        [("1\n", "1"), ("4\n", "2"), ("8\n", "92"), ("10\n", "724")],
    )

    _hidden(
        40, "coding_0234",
        "Write program.py. It reads a single arithmetic expression with "
        "non-negative integers, spaces, parentheses, and the operators +, - "
        "and *. All intermediate values are non-negative. Print its integer "
        "value. Work only inside the current directory. When you are done, "
        "write ONLY the word DONE to answer.txt.",
        8,
        "import sys\n\ndef main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
        '''import sys


def evaluate(text):
    position = 0

    def parse_expression():
        nonlocal position
        value = parse_term()
        while position < len(text) and text[position] in "+-":
            operator = text[position]
            position += 1
            right = parse_term()
            value = value + right if operator == "+" else value - right
        return value

    def parse_term():
        nonlocal position
        value = parse_factor()
        while position < len(text) and text[position] == "*":
            position += 1
            value *= parse_factor()
        return value

    def parse_factor():
        nonlocal position
        while position < len(text) and text[position] == " ":
            position += 1
        if text[position] == "(":
            position += 1
            value = parse_expression()
            while text[position] == " ":
                position += 1
            position += 1
            return value
        start = position
        while position < len(text) and text[position].isdigit():
            position += 1
        return int(text[start:position])

    return parse_expression()


def main():
    text = sys.stdin.read().strip().replace(" ", "")
    if text:
        print(evaluate(text))


if __name__ == "__main__":
    main()
''',
        [
            ("2 + 3 * 4\n", "14"),
            ("(2 + 3) * 4\n", "20"),
            ("100 - 20 - 5\n", "75"),
            ("2 * (3 + (4 - 1)) * 5\n", "60"),
        ],
    )


if __name__ == "__main__":
    generate()
