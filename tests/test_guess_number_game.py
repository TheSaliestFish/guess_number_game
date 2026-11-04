import unittest
from unittest.mock import patch

import guess_number_game


class GameTests(unittest.TestCase):
    def test_game_retries_and_counts_only_integer_guesses(self):
        guesses = iter(("not a number", "3", "7", "5"))
        output = []

        with patch.object(guess_number_game.random, "randint", return_value=5):
            guess_number_game.play(
                1,
                10,
                "en",
                input_fn=lambda _prompt: next(guesses),
                print_fn=output.append,
            )

        self.assertIn("Please enter a valid integer.", output)
        self.assertIn("Too low. Try again!", output)
        self.assertIn("Too high. Try again!", output)
        self.assertIn(
            "Congratulations! You guessed it in 3 attempts.",
            output,
        )

    def test_game_uses_chinese_messages(self):
        with patch.object(guess_number_game.random, "randint", return_value=4):
            guess_number_game.play(
                4,
                8,
                "zh",
                input_fn=lambda _prompt: "4",
                print_fn=lambda message: self.assertTrue(
                    any("\u4e00" <= char <= "\u9fff" for char in message)
                ),
            )

    def test_parser_defaults_and_options(self):
        parser = guess_number_game.build_parser()
        defaults = parser.parse_args([])
        options = parser.parse_args(
            ["--min", "-5", "--max", "20", "-l", "en"]
        )

        self.assertEqual((defaults.minimum, defaults.maximum, defaults.language), (1, 100, "zh"))
        self.assertEqual((options.minimum, options.maximum, options.language), (-5, 20, "en"))

    def test_main_rejects_invalid_range(self):
        with self.assertRaises(SystemExit) as error:
            guess_number_game.main(["--min", "5", "--max", "5"])

        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
