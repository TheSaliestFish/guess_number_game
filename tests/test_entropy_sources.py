import unittest
from unittest.mock import patch

from guess_number_game import transport
from guess_number_game.entropy import (
    DEFAULT_GROUP,
    GROUPS,
    GROUP_KEYS,
    label,
)
from guess_number_game.entropy.anu import AnuQrngSource
from guess_number_game.entropy.chainlink_vrf import ChainlinkVrfSource
from guess_number_game.entropy.csrng import CsrngSource
from guess_number_game.entropy.curby import CHAIN_CID, CurbySource
from guess_number_game.entropy.drand import DrandSource
from guess_number_game.entropy.local import LocalSource
from guess_number_game.entropy.nist import NistBeaconSource
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


class CsrngTests(unittest.TestCase):
    def test_reads_the_random_field(self):
        payload = [{"status": "success", "min": 1, "max": 10, "random": 7}]
        with patch.object(transport, "get_json", return_value=payload) as get_json:
            self.assertEqual(CsrngSource().fetch(1, 10, DEADLINE), 7)

        self.assertIn("min=1", get_json.call_args[0][0])
        self.assertIn("max=10", get_json.call_args[0][0])

    def test_failed_status_raises(self):
        with patch.object(transport, "get_json", return_value=[{"status": "error"}]):
            with self.assertRaises(ValueError):
                CsrngSource().fetch(1, 10, DEADLINE)


class NistBeaconTests(unittest.TestCase):
    def test_uses_the_pulse_output_value(self):
        pulse = {"pulse": {"outputValue": "00" * 64}}
        with patch.object(transport, "get_json", return_value=pulse):
            self.assertEqual(NistBeaconSource().fetch(1, 100, DEADLINE), 1)

    def test_missing_output_value_raises(self):
        with patch.object(transport, "get_json", return_value={"pulse": {}}):
            with self.assertRaises(KeyError):
                NistBeaconSource().fetch(1, 100, DEADLINE)


class DrandTests(unittest.TestCase):
    def test_uses_the_round_randomness(self):
        payload = {"round": 1, "randomness": "00" * 32}
        with patch.object(transport, "get_json", return_value=payload):
            self.assertEqual(DrandSource().fetch(1, 100, DEADLINE), 1)

    def test_endpoint_is_injectable(self):
        with patch.object(transport, "get_json", return_value={"randomness": "00" * 32}) as get_json:
            DrandSource(url="https://mirror.test/latest").fetch(1, 100, DEADLINE)

        self.assertEqual(get_json.call_args[0][0], "https://mirror.test/latest")


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
        with patch.object(transport, "get_json", return_value=pulse) as get_json:
            value = CurbySource().fetch(1, 100, DEADLINE)

        self.assertTrue(1 <= value <= 100)
        self.assertIn(CHAIN_CID, get_json.call_args[0][0])


class ChainlinkVrfTests(unittest.TestCase):
    def test_reads_the_word_returned_by_eth_call(self):
        source = ChainlinkVrfSource(
            rpc_url="https://rpc.test", contract="0xabc", calldata="0xdeadbeef"
        )
        response = {"result": "0x" + "00" * 31 + "2a"}

        with patch.object(transport, "post_json", return_value=response) as post_json:
            value = source.fetch(1, 100, DEADLINE)

        self.assertEqual(value, 43)
        rpc_url, payload = post_json.call_args[0][0], post_json.call_args[0][1]
        self.assertEqual(rpc_url, "https://rpc.test")
        self.assertEqual(payload["method"], "eth_call")
        self.assertEqual(payload["params"][0], {"to": "0xabc", "data": "0xdeadbeef"})

    def test_without_configuration_it_is_unavailable(self):
        source = ChainlinkVrfSource(environ={})

        with self.assertRaises(ValueError):
            source.fetch(1, 100, DEADLINE)

    def test_empty_result_raises(self):
        source = ChainlinkVrfSource(rpc_url="https://rpc.test", contract="0xabc")

        with patch.object(transport, "post_json", return_value={"result": "0x"}):
            with self.assertRaises(ValueError):
                source.fetch(1, 100, DEADLINE)


class LocalTests(unittest.TestCase):
    def test_never_leaves_the_requested_range(self):
        source = LocalSource()

        for _ in range(50):
            self.assertTrue(1 <= source.fetch(1, 6, DEADLINE) <= 6)


class GroupTests(unittest.TestCase):
    def test_three_groups_with_the_expected_sources(self):
        self.assertEqual(set(GROUP_KEYS), {"beacon", "trng", "vrf"})
        self.assertEqual(
            [source.key for source in GROUPS["beacon"]], ["nist", "drand", "curby"]
        )
        self.assertEqual(
            [source.key for source in GROUPS["trng"]], ["randomorg", "qrng", "csrng"]
        )
        self.assertEqual([source.key for source in GROUPS["vrf"]], ["chainlink"])
        self.assertEqual(DEFAULT_GROUP, "trng")

    def test_every_group_has_labels(self):
        for key in GROUP_KEYS:
            for language in ("zh", "en"):
                self.assertTrue(label(key, language))
