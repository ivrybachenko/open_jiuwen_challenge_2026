import unittest
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
