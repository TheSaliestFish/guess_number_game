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


def _open(url, deadline, data=None, headers=None):
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": USER_AGENT, **(headers or {})},
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=deadline.remaining) as response:
        return response.read().decode("utf-8")


def get(url, deadline, headers=None):
    """Return the response body for `url`, giving up when `deadline` expires."""
    return _open(url, deadline, headers=headers)


def get_json(url, deadline, headers=None):
    """Like `get`, but parse the body as JSON."""
    return json.loads(get(url, deadline, headers))


def post_json(url, payload, deadline, headers=None):
    """POST `payload` as JSON and parse the JSON response."""
    body = json.dumps(payload).encode("utf-8")
    response = _open(
        url,
        deadline,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    return json.loads(response)
