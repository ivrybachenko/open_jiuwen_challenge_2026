"""Unit tests for the contest token accounting."""

from __future__ import annotations

import unittest

from harness.application.llm import token_cost


class TokenCostTest(unittest.TestCase):
    def test_output_only(self) -> None:
        self.assertEqual(token_cost(0, 10), 10)

    def test_input_is_divided_by_ten_and_rounded_up(self) -> None:
        self.assertEqual(token_cost(1, 0), 1)
        self.assertEqual(token_cost(9, 0), 1)
        self.assertEqual(token_cost(10, 0), 1)
        self.assertEqual(token_cost(11, 0), 2)

    def test_mixed_usage(self) -> None:
        self.assertEqual(token_cost(100, 20), 30)

    def test_negative_counts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            token_cost(-1, 0)
        with self.assertRaises(ValueError):
            token_cost(0, -1)


if __name__ == "__main__":
    unittest.main()
