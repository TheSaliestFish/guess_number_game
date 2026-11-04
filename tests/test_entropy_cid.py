import unittest

from guess_number_game.entropy.cid import digest

CURBY_PULSE_CID = (
    "bafyriqci6f3st2mg7gq733ho4zvvth32zpy2mtiylixwmhoz6d627eo3jfpmbxepe"
    "54u2zdvymonq5sp3armtm4rodxsynsirr5g3xsbd3q4s"
)


class CidTests(unittest.TestCase):
    def test_sha3_512_digest_is_extracted(self):
        self.assertEqual(len(digest(CURBY_PULSE_CID)), 64)

    def test_unsupported_multibase_is_rejected(self):
        with self.assertRaises(ValueError):
            digest("zdj7WkRPAX9o9nb9zPbXzwG7JEs78uyhwbUs8JSUayB98DWWY")

    def test_truncated_multihash_is_rejected(self):
        with self.assertRaises(ValueError):
            digest("b")
