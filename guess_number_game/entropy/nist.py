"""NIST Randomness Beacon adapter: signed 512-bit pulses every 60 seconds."""

from .. import transport
from .base import RandomSource
from .mapping import pick_from_bytes

PULSE_URL = "https://beacon.nist.gov/beacon/2.0/pulse/last"


class NistBeaconSource(RandomSource):
    key = "nist"
    labels = {"zh": "NIST 随机信标", "en": "NIST randomness beacon"}

    def fetch(self, minimum, maximum, deadline):
        pulse = transport.get_json(PULSE_URL, deadline)["pulse"]
        return pick_from_bytes(bytes.fromhex(pulse["outputValue"]), minimum, maximum)
