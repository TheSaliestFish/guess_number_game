"""Uniform mapping from random bytes onto an inclusive integer range."""


def pick_from_bytes(data, minimum, maximum):
    """Map uniform random bytes onto [minimum, maximum] without modulo bias.

    Rejection sampling: values above the largest multiple of the range are
    discarded instead of being folded back, which would skew small ranges.
    """
    span = maximum - minimum + 1
    if span <= 1:
        return minimum
    bits = len(data) * 8
    limit = (1 << bits) - ((1 << bits) % span)
    value = int.from_bytes(data, "big")
    if value >= limit:
        raise ValueError("random bytes fall outside the usable range")
    return minimum + value % span
