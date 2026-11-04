"""Local pseudo-randomness: the offline source and the fallback path."""

import random

from .base import RandomSource


def random_in_range(minimum, maximum):
    """Local PRNG value in [minimum, maximum]."""
    return random.randint(minimum, maximum)


class LocalSource(RandomSource):
    """No network access at all."""

    key = "local"
    labels = {"zh": "本地伪随机", "en": "local PRNG"}

    def fetch(self, minimum, maximum, deadline):
        return random_in_range(minimum, maximum)
