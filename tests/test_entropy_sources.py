import unittest
from unittest.mock import patch

from guess_number_game import transport
from guess_number_game.entropy import SOURCES, SOURCE_KEYS, draw, label
from guess_number_game.entropy.anu import AnuQrngSource
from guess_number_game.entropy.base import SourceUnavailable
from guess_number_game.entropy.curby import CHAIN_CID, CurbySource
from guess_number_game.entropy.local import LocalSource
from guess_number_game.entropy.random_org import RandomOrgSource

DEADLINE = transport.Deadline(1.0)


class RandomOrgTests(unittest.TestCase):
    def test_parses_the_plain_integer_response(self):
        with patch.object(transport, "get", return_value="7\n"):
            self.assertEqual(RandomOrgSource().fetch(1, 100, DEADLINE), 7)

    def test_rejects_out_of_range_values(self):
        with patch.object(transport, "get", return_value="99\n"):
            with self.assertRaises(ValueError):
                RandomOrgSource().fetch(1, 10, DEADLINE)


class AnuQrngTests(unittest.TestCase):
    def test_maps_quantum_bytes_into_the_range(self):
        payload = {"success": True, "data": [0] * 64}
        with patch.object(transport, "get_json", return_value=payload):
            self.assertEqual(AnuQrngSource().fetch(1, 100, DEADLINE), 1)

    def test_unusable_payload_raises(self):
        with patch.object(transport, "get_json", return_value={"success": False}):
            with self.assertRaises(ValueError):
                AnuQrngSource().fetch(1, 100, DEADLINE)


class CurbyTests(unittest.TestCase):
    def test_uses_the_latest_pulse_digest(self):
        pulse = {
            "cid": {
                "/": (
                    "bafyriqci6f3st2mg7gq733ho4zvvth32zpy2mtiylixwmhoz6d627eo3jf"
                    "pmbxepe54u2zdvymonq5sp3armtm4rodxsynsirr5g3xsbd3q4s"
                )
            }
        }
        source = CurbySource()

        with patch.object(transport, "get_json", return_value=pulse) as get_json:
            value = source.fetch(1, 100, DEADLINE)

        self.assertTrue(1 <= value <= 100)
        self.assertIn(CHAIN_CID, get_json.call_args[0][0])

    def test_chain_and_host_are_injectable(self):
        source = CurbySource(base_url="https://example.test", chain_cid="bafy-test")

        with patch.object(
            transport, "get_json", return_value={"cid": {"/": "b" + "a" * 100}}
        ) as get_json:
            with self.assertRaises(ValueError):
                source.fetch(1, 100, DEADLINE)

        self.assertEqual(
            get_json.call_args[0][0],
            "https://example.test/chains/bafy-test/pulses/latest",
        )


class LocalTests(unittest.TestCase):
    def test_never_leaves_the_requested_range(self):
        source = LocalSource()

        for _ in range(50):
            self.assertTrue(1 <= source.fetch(1, 6, DEADLINE) <= 6)


class RegistryTests(unittest.TestCase):
    def test_registry_exposes_every_source_with_labels(self):
        self.assertEqual(set(SOURCE_KEYS), {"qrng", "randomorg", "curby", "local"})
        for key in SOURCE_KEYS:
            for language in ("zh", "en"):
                self.assertTrue(label(key, language))

    def test_draw_normalises_adapter_failures(self):
        with patch.object(SOURCES["randomorg"], "fetch", side_effect=OSError("offline")):
            with self.assertRaises(SourceUnavailable) as raised:
                draw("randomorg", 1, 10, DEADLINE)

        self.assertEqual(raised.exception.source_key, "randomorg")

    def test_draw_returns_the_adapter_value(self):
        with patch.object(SOURCES["curby"], "fetch", return_value=5):
            self.assertEqual(draw("curby", 1, 10, DEADLINE), 5)
