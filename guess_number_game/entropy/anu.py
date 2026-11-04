"""ANU QRNG adapter: 64 bytes of quantum vacuum fluctuation entropy."""

from .. import transport
from .base import RandomSource
from .mapping import pick_from_bytes

API_URL = "https://qrng.anu.edu.au/API/jsonI.php?length=64&type=uint8"


class AnuQrngSource(RandomSource):
    key = "qrng"
    labels = {
        "zh": "量子真空涨落（ANU QRNG）",
        "en": "ANU QRNG (quantum vacuum fluctuations)",
    }

    def fetch(self, minimum, maximum, deadline):
        payload = transport.get_json(API_URL, deadline)
        data = payload.get("data")
        if not payload.get("success", True) or not data:
            raise ValueError("ANU QRNG returned no random data")
        return pick_from_bytes(bytes(data), minimum, maximum)
