import unittest

from guess_number_game.entropy.mapping import pick_from_bytes


class MappingTests(unittest.TestCase):
    def test_bytes_map_onto_the_lower_bound_plus_remainder(self):
        data = (42).to_bytes(64, "big")

        self.assertEqual(pick_from_bytes(data, 1, 100), 43)
        self.assertEqual(pick_from_bytes(data, 0, 1), 0)
        self.assertEqual(pick_from_bytes(b"\x00" * 64, 1, 100), 1)

    def test_single_value_range_is_returned_unchanged(self):
        self.assertEqual(pick_from_bytes(b"\xff" * 64, 7, 7), 7)

    def test_bytes_beyond_the_unbiased_limit_are_rejected(self):
        # 2**512 - 1 sits exactly on the rejection boundary for a span of 3.
        with self.assertRaises(ValueError):
            pick_from_bytes(b"\xff" * 64, 1, 3)
