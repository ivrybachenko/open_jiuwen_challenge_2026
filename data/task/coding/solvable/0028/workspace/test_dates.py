import unittest
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
