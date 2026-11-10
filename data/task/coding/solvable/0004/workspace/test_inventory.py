import unittest

import inventory


class T(unittest.TestCase):
    def test_default_bucket_starts_empty(self):
        self.assertEqual(inventory.add_item("apple"), ["apple"])

    def test_default_buckets_are_independent(self):
        self.assertEqual(inventory.add_item("pear"), ["pear"])

    def test_explicit_bucket_is_used(self):
        bucket = ["x"]
        result = inventory.add_item("y", bucket)
        self.assertEqual(result, ["x", "y"])
        self.assertIs(result, bucket)

    def test_clear_returns_empty(self):
        self.assertEqual(inventory.clear_bucket(), [])

    def test_clear_does_not_touch_a_passed_bucket(self):
        bucket = ["z"]
        result = inventory.clear_bucket(bucket)
        self.assertEqual(result, [])
        self.assertIs(result, bucket)


if __name__ == "__main__":
    unittest.main()
