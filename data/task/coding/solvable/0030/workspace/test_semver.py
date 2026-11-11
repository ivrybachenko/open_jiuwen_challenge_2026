import unittest
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
