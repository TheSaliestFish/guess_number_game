"""Randomness sources: a registry plus one uniform draw entry point."""

from .anu import AnuQrngSource
from .base import FETCH_ERRORS, RandomSource, SourceUnavailable
from .curby import CurbySource
from .local import LocalSource, random_in_range
from .random_org import RandomOrgSource

SOURCES = {
    source.key: source
    for source in (AnuQrngSource(), RandomOrgSource(), CurbySource(), LocalSource())
}

SOURCE_KEYS = tuple(SOURCES)
DEFAULT_SOURCE = "qrng"


def draw(source_key, minimum, maximum, deadline):
    """Draw from `source_key`, normalising adapter failures into SourceUnavailable."""
    try:
        return SOURCES[source_key].fetch(minimum, maximum, deadline)
    except FETCH_ERRORS as cause:
        raise SourceUnavailable(source_key) from cause


def label(source_key, language):
    """Localized display name of a source."""
    return SOURCES[source_key].label(language)


__all__ = [
    "DEFAULT_SOURCE",
    "FETCH_ERRORS",
    "RandomSource",
    "SOURCES",
    "SOURCE_KEYS",
    "SourceUnavailable",
    "draw",
    "label",
    "random_in_range",
]
