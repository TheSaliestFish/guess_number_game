import threading
import time
import unittest

from guess_number_game.entropy import fanout
from guess_number_game.entropy.base import RandomSource, SourceUnavailable
from guess_number_game.transport import Deadline


class FakeSource(RandomSource):
    def __init__(self, key, value=None, delay=0.0, error=None, started=None):
        self.key = key
        self.labels = {"zh": key, "en": key}
        self._value = value
        self._delay = delay
        self._error = error
        self._started = started

    def fetch(self, minimum, maximum, deadline):
        if self._started is not None:
            self._started.set()
        if self._delay:
            time.sleep(self._delay)
        if self._error is not None:
            raise self._error
        return self._value


class FanoutTests(unittest.TestCase):
    def test_returns_the_first_successful_answer(self):
        sources = [
            FakeSource("slow-fail", delay=0.2, error=OSError("offline")),
            FakeSource("fast", value=7),
        ]

        value = fanout.draw("trng", sources, 1, 10, Deadline(0.6))

        self.assertEqual(value, 7)

    def test_every_source_gets_a_request(self):
        events = [threading.Event() for _ in range(3)]
        sources = [
            FakeSource("one", value=1, started=events[0]),
            FakeSource("two", value=2, started=events[1]),
            FakeSource("three", value=3, started=events[2]),
        ]

        value = fanout.draw("trng", sources, 1, 10, Deadline(0.6))

        self.assertIn(value, (1, 2, 3))
        self.assertTrue(all(event.is_set() for event in events))

    def test_raises_when_no_source_answers_in_time(self):
        sources = [FakeSource("slow", delay=0.5, value=1)]

        started = time.monotonic()
        with self.assertRaises(SourceUnavailable):
            fanout.draw("trng", sources, 1, 10, Deadline(0.1))

        self.assertLess(time.monotonic() - started, 0.4)

    def test_raises_when_every_source_fails(self):
        sources = [
            FakeSource("a", error=OSError("down")),
            FakeSource("b", error=ValueError("bad payload")),
        ]

        with self.assertRaises(SourceUnavailable) as raised:
            fanout.draw("beacon", sources, 1, 10, Deadline(0.5))

        self.assertEqual(raised.exception.source_key, "beacon")

    def test_empty_group_is_unavailable(self):
        with self.assertRaises(SourceUnavailable):
            fanout.draw("vrf", [], 1, 10, Deadline(0.5))
