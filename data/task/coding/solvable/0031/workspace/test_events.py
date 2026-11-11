import unittest
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
