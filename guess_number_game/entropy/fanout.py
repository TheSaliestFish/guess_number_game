"""Parallel fan-out across the sources of one category."""

import queue
import threading
import time

from .base import FETCH_ERRORS, SourceUnavailable


def draw(group_key, sources, minimum, maximum, deadline):
    """Ask every source at once and return the first value that arrives.

    One daemon thread is started per source, so a request still in flight never
    delays process exit once the game already has its answer. The timeout window
    starts when the last request has been dispatched, which keeps the budget
    shared across three concurrent sources instead of stacking up.
    """
    if not sources:
        raise SourceUnavailable(group_key)

    answers = queue.Queue()

    def worker(source):
        try:
            answers.put(source.fetch(minimum, maximum, deadline))
        except FETCH_ERRORS:
            answers.put(None)

    threads = [
        threading.Thread(target=worker, args=(source,), daemon=True)
        for source in sources
    ]
    for thread in threads:
        thread.start()

    try:
        expires_at = time.monotonic() + deadline.remaining
    except TimeoutError:
        raise SourceUnavailable(group_key) from None

    failures = 0
    while True:
        remaining = expires_at - time.monotonic()
        if remaining <= 0:
            raise SourceUnavailable(group_key)
        try:
            value = answers.get(timeout=remaining)
        except queue.Empty:
            raise SourceUnavailable(group_key) from None
        if value is not None:
            return value
        failures += 1
        if failures >= len(sources):
            raise SourceUnavailable(group_key)
