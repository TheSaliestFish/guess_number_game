"""Game rules: drawing the answer (with fallback) and running one round.

This module knows nothing about argparse, HTTP details or individual sources.
"""

from . import entropy
from .messages import text

DEFAULT_TIMEOUT = 2.0


def draw_answer(
    group_key,
    minimum,
    maximum,
    language,
    notify=print,
    timeout=DEFAULT_TIMEOUT,
):
    """Draw the secret number, falling back to local randomness when every source fails."""
    try:
        return entropy.draw(group_key, minimum, maximum, timeout)
    except entropy.SourceUnavailable:
        notify(text(language, "fallback", source=entropy.label(group_key, language)))
        return entropy.random_in_range(minimum, maximum)


def play(minimum, maximum, language, answer, input_fn=input, print_fn=print):
    """Run one round against a pre-drawn `answer`."""
    attempts = 0
    print_fn(text(language, "intro", minimum=minimum, maximum=maximum))

    while True:
        try:
            guess = int(input_fn(text(language, "prompt")))
        except ValueError:
            print_fn(text(language, "invalid"))
            continue
        except EOFError:
            print_fn(text(language, "aborted"))
            return

        attempts += 1
        if guess < answer:
            print_fn(text(language, "low"))
        elif guess > answer:
            print_fn(text(language, "high"))
        else:
            print_fn(text(language, "won", attempts=attempts))
            return
