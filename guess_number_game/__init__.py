"""猜数字游戏 | Guess the Number: a CLI game with pluggable randomness sources."""

from .cli import build_parser, main
from .game import draw_answer, play
from .messages import LANGUAGES, MESSAGES

__all__ = [
    "LANGUAGES",
    "MESSAGES",
    "build_parser",
    "draw_answer",
    "main",
    "play",
]
