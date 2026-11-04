"""Minimal, deadline-bound HTTP helpers used by the entropy adapters."""

import json
import time
import urllib.request

USER_AGENT = "guess-number-game/1.2"


class Deadline:
    """A single wall-clock budget shared by every request of one lookup."""

    def __init__(self, seconds):
        self._expires_at = time.monotonic() + seconds

    @property
    def remaining(self):
        """Seconds left in the budget; raises TimeoutError once it is spent."""
        left = self._expires_at - time.monotonic()
        if left <= 0:
            raise TimeoutError("randomness request timed out")
        return left


def get(url, deadline, headers=None):
    """Return the response body for `url`, giving up when `deadline` expires."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, **(headers or {})},
    )
    with urllib.request.urlopen(request, timeout=deadline.remaining) as response:
        return response.read().decode("utf-8")


def get_json(url, deadline, headers=None):
    """Like `get`, but parse the body as JSON."""
    return json.loads(get(url, deadline, headers))
