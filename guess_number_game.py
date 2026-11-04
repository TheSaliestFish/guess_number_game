"""Script entry point kept for `python guess_number_game.py`.

The implementation lives in the :mod:`guess_number_game` package; this shim only
forwards to its CLI so older instructions and the release build keep working.
"""

from guess_number_game.cli import main

if __name__ == "__main__":
    main()
