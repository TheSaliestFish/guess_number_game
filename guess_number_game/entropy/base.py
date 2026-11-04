"""The contract every randomness source implements."""

import http.client

# Failures that simply mean "this source cannot answer right now".
FETCH_ERRORS = (OSError, ValueError, TypeError, IndexError, http.client.HTTPException)


class SourceUnavailable(Exception):
    """Raised when a randomness source cannot produce a value."""

    def __init__(self, source_key):
        super().__init__(source_key)
        self.source_key = source_key


class RandomSource:
    """A pluggable provider of one uniformly random integer in a range."""

    key = ""
    labels = {}

    def label(self, language):
        """Human-readable source name for notices."""
        return self.labels.get(language) or self.labels["en"]

    def fetch(self, minimum, maximum, deadline):
        """Return an integer in [minimum, maximum] or raise one of FETCH_ERRORS."""
        raise NotImplementedError
