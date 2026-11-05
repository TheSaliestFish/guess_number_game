"""CSRNG.net adapter: a lightweight HTTP endpoint for NIST-certified RNG hardware."""

from .. import transport
from .base import RandomSource

CSRNG_URL = "https://csrng.net/csrng/csrng.php?min={minimum}&max={maximum}"


class CsrngSource(RandomSource):
    key = "csrng"
    labels = {"zh": "CSRNG Lite", "en": "CSRNG Lite"}

    def fetch(self, minimum, maximum, deadline):
        payload = transport.get_json(
            CSRNG_URL.format(minimum=minimum, maximum=maximum), deadline
        )
        entry = payload[0] if isinstance(payload, list) and payload else None
        if not entry or entry.get("status") != "success":
            raise ValueError("CSRNG returned no random value")
        value = int(entry["random"])
        if not minimum <= value <= maximum:
            raise ValueError("CSRNG returned an out-of-range value")
        return value
