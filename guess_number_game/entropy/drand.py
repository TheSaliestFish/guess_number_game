"""drand (League of Entropy) adapter: threshold-BLS verifiable randomness."""

from .. import transport
from .base import RandomSource
from .mapping import pick_from_bytes

LATEST_URL = "https://api.drand.sh/public/latest"


class DrandSource(RandomSource):
    key = "drand"
    labels = {"zh": "drand / League of Entropy", "en": "drand / League of Entropy"}

    def __init__(self, url=LATEST_URL):
        self._url = url

    def fetch(self, minimum, maximum, deadline):
        randomness = transport.get_json(self._url, deadline)["randomness"]
        return pick_from_bytes(bytes.fromhex(randomness), minimum, maximum)
