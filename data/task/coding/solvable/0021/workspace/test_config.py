import unittest
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
        self.assertEqual(parse_config("\n# only a comment\n"), {})


if __name__ == "__main__":
    unittest.main()
