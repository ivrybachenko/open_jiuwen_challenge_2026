import unittest

from duration import parse_duration


class T(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(parse_duration("45s"), 45)

    def test_minutes(self):
        self.assertEqual(parse_duration("2m"), 120)

    def test_hours(self):
        self.assertEqual(parse_duration("3h"), 10800)

    def test_compact(self):
        self.assertEqual(parse_duration("1h30m"), 5400)

    def test_spaces(self):
        self.assertEqual(parse_duration("2h 15m 10s"), 8110)

    def test_zero(self):
        self.assertEqual(parse_duration("0s"), 0)

    def test_invalid(self):
        for bad in ["", "abc", "10x", "1h 30"]:
            with self.assertRaises(ValueError):
                parse_duration(bad)


if __name__ == "__main__":
    unittest.main()
