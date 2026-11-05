"""Command line interface: argument parsing and wiring only."""

import argparse

from . import __version__, entropy
from .game import draw_answer, play
from .messages import LANGUAGES


def build_parser():
    parser = argparse.ArgumentParser(
        prog="guess_number_game",
        description="Play a number guessing game in Chinese or English.",
    )
    parser.add_argument(
        "--min",
        dest="minimum",
        type=int,
        default=1,
        help="minimum number (default: 1)",
    )
    parser.add_argument(
        "--max",
        dest="maximum",
        type=int,
        default=100,
        help="maximum number (default: 100)",
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=LANGUAGES,
        default="zh",
        help="game language: zh or en (default: zh)",
    )
    parser.add_argument(
        "-s",
        "--source",
        choices=entropy.GROUP_KEYS,
        default=entropy.DEFAULT_GROUP,
        help=(
            "randomness family: beacon (NIST/drand/CURBy), trng (Random.org/ANU/CSRNG), "
            "vrf (Chainlink VRF) (default: %(default)s)"
        ),
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.minimum >= args.maximum:
        parser.error("--min must be less than --max")
    answer = draw_answer(args.source, args.minimum, args.maximum, args.language)
    play(args.minimum, args.maximum, args.language, answer)
