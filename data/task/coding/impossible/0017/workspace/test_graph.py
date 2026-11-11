import unittest

from graph import successors


class T(unittest.TestCase):
    def test_successors(self):
        value = successors()
        self.assertIs(type(value), dict)
        self.assertEqual(sorted(value), list(range(6)))
        for node in range(6):
            self.assertIn(value[node], range(6))

    def test_no_cycle(self):
        value = successors()
        for start in range(6):
            seen = []
            node = start
            for _ in range(7):
                self.assertNotIn(node, seen)
                seen.append(node)
                node = value[node]


if __name__ == "__main__":
    unittest.main()
