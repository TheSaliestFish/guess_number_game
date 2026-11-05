"""Randomness sources grouped into three families, plus one draw entry point.

Groups are queried in parallel: every source of the chosen category gets its
own request thread, and the first answer wins within a shared time budget.
"""

from ..transport import Deadline
from . import fanout
from .anu import AnuQrngSource
from .base import FETCH_ERRORS, RandomSource, SourceUnavailable
from .chainlink_vrf import ChainlinkVrfSource
from .csrng import CsrngSource
from .curby import CurbySource
from .drand import DrandSource
from .local import LocalSource, random_in_range
from .nist import NistBeaconSource
from .random_org import RandomOrgSource

GROUPS = {
    "beacon": (NistBeaconSource(), DrandSource(), CurbySource()),
    "trng": (RandomOrgSource(), AnuQrngSource(), CsrngSource()),
    "vrf": (ChainlinkVrfSource(),),
}

GROUP_KEYS = tuple(GROUPS)
DEFAULT_GROUP = "trng"

GROUP_LABELS = {
    "beacon": {
        "zh": "可验证随机信标（NIST / drand / CURBy）",
        "en": "verifiable randomness beacons (NIST / drand / CURBy)",
    },
    "trng": {
        "zh": "真随机 / 量子随机 API（Random.org / ANU QRNG / CSRNG）",
        "en": "true and quantum randomness APIs (Random.org / ANU QRNG / CSRNG)",
    },
    "vrf": {
        "zh": "Web3 可验证随机函数（Chainlink VRF）",
        "en": "Web3 verifiable random function (Chainlink VRF)",
    },
}


def draw(group_key, minimum, maximum, timeout):
    """Fan out across one category and return the first value, or raise SourceUnavailable."""
    deadline = Deadline(timeout)
    return fanout.draw(group_key, GROUPS[group_key], minimum, maximum, deadline)


def label(group_key, language):
    """Localized display name of a category."""
    labels = GROUP_LABELS[group_key]
    return labels.get(language) or labels["en"]


__all__ = [
    "DEFAULT_GROUP",
    "FETCH_ERRORS",
    "GROUPS",
    "GROUP_KEYS",
    "GROUP_LABELS",
    "RandomSource",
    "SourceUnavailable",
    "draw",
    "label",
    "random_in_range",
]
