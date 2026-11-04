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

    def test_source_option_defaults_to_qrng(self):
        parser = guess_number_game.build_parser()

        self.assertEqual(parser.parse_args([]).source, "qrng")
        self.assertEqual(
            parser.parse_args(["-s", "curby"]).source, "curby"
        )

    def test_choose_answer_uses_remote_source(self):
        fetcher = lambda minimum, maximum, deadline: maximum
        with patch.dict(guess_number_game.SOURCE_FETCHERS, {"randomorg": fetcher}):
            answer = guess_number_game.choose_answer(
                1, 10, "randomorg", "en", print_fn=lambda _message: None
            )

        self.assertEqual(answer, 10)

    def test_choose_answer_falls_back_to_local_when_source_fails(self):
        output = []

        def slow_source(minimum, maximum, deadline):
            raise TimeoutError("randomness request timed out")

        with patch.dict(guess_number_game.SOURCE_FETCHERS, {"qrng": slow_source}):
            with patch.object(guess_number_game.random, "randint", return_value=3):
                answer = guess_number_game.choose_answer(
                    1, 10, "qrng", "zh", print_fn=output.append
                )

        self.assertEqual(answer, 3)
        self.assertEqual(len(output), 1)
        self.assertIn("量子真空涨落", output[0])
        self.assertIn("本地随机数", output[0])

    def test_choose_answer_local_does_not_touch_the_network(self):
        with patch.dict(guess_number_game.SOURCE_FETCHERS, {}, clear=True):
            with patch.object(guess_number_game.random, "randint", return_value=7):
                answer = guess_number_game.choose_answer(
                    1, 10, "local", "zh", print_fn=lambda _message: None
                )

        self.assertEqual(answer, 7)

    def test_play_stops_cleanly_when_input_ends(self):
        output = []

        def no_more_input(_prompt):
            raise EOFError()

        with patch.object(guess_number_game.random, "randint", return_value=5):
            guess_number_game.play(
                1, 10, "en", input_fn=no_more_input, print_fn=output.append
            )

        self.assertEqual(output[-1], "Input ended, stopping the game.")

    def test_pick_from_bytes_maps_value_into_range(self):
        data = (42).to_bytes(64, "big")

        self.assertEqual(guess_number_game._pick_from_bytes(data, 1, 100), 43)
        self.assertEqual(guess_number_game._pick_from_bytes(data, 0, 1), 0)
        self.assertEqual(guess_number_game._pick_from_bytes(b"\x00" * 64, 7, 7), 7)

    def test_cid_digest_reads_the_curby_pulse_digest(self):
        cid = (
            "bafyriqci6f3st2mg7gq733ho4zvvth32zpy2mtiylixwmhoz6d627eo3jfpmbxepe"
            "54u2zdvymonq5sp3armtm4rodxsynsirr5g3xsbd3q4s"
        )

        self.assertEqual(len(guess_number_game._cid_digest(cid)), 64)


if __name__ == "__main__":
    unittest.main()
