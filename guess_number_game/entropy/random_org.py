"""Random.org adapter: atmospheric noise."""

from .. import transport
from .base import RandomSource

INTEGERS_URL = (
    "https://www.random.org/integers/?num=1&min={minimum}&max={maximum}"
    "&col=1&base=10&format=plain&rnd=new"
)


class RandomOrgSource(RandomSource):
    key = "randomorg"
    labels = {"zh": "Random.org 大气噪声", "en": "Random.org atmospheric noise"}

    def fetch(self, minimum, maximum, deadline):
        url = INTEGERS_URL.format(minimum=minimum, maximum=maximum)
        value = int(transport.get(url, deadline).strip())
        if not minimum <= value <= maximum:
            raise ValueError("Random.org returned an out-of-range value")
        return value
