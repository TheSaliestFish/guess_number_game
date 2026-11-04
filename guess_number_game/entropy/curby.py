"""CURBy adapter: the Bell-test quantum random beacon published on a twine spool."""

from .. import transport
from .base import RandomSource
from .cid import digest
from .mapping import pick_from_bytes

API_URL = "https://api.entwine.me"
# The CURBy-RNG chain, as listed by GET https://api.entwine.me/chains.
CHAIN_CID = (
    "bafyriqci6f3st2mg7gq733ho4zvvth32zpy2mtiylixwmhoz6d627eo3jfpmbxepe"
    "54u2zdvymonq5sp3armtm4rodxsynsirr5g3xsbd3q4s"
)


class CurbySource(RandomSource):
    key = "curby"
    labels = {
        "zh": "CURBy 贝尔测试量子随机信标",
        "en": "CURBy Bell-test quantum random beacon",
    }

    def __init__(self, base_url=API_URL, chain_cid=CHAIN_CID):
        self._base_url = base_url
        self._chain_cid = chain_cid

    def fetch(self, minimum, maximum, deadline):
        url = "{base}/chains/{chain}/pulses/latest".format(
            base=self._base_url, chain=self._chain_cid
        )
        pulse = transport.get_json(url, deadline)
        return pick_from_bytes(digest(pulse["cid"]["/"]), minimum, maximum)
