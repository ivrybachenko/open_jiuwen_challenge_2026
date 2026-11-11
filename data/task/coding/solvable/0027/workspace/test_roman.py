import unittest
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
