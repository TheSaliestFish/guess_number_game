import unittest
from unittest.mock import patch

from guess_number_game import entropy, game


def _feed(*values):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


class PlayTests(unittest.TestCase):
    def test_counts_only_valid_guesses_and_wins(self):
        output = []

        game.play(1, 10, "en", 5, input_fn=_feed("nope", "3", "7", "5"), print_fn=output.append)

        self.assertEqual(output[0], "Guess the number: enter an integer between 1 and 10.")
        self.assertIn("Please enter a valid integer.", output)
        self.assertIn("Too low. Try again!", output)
        self.assertIn("Too high. Try again!", output)
        self.assertEqual(output[-1], "Congratulations! You guessed it in 3 attempts.")

    def test_stops_cleanly_when_input_ends(self):
        output = []

        def no_more_input(_prompt):
            raise EOFError()

        game.play(1, 10, "en", 5, input_fn=no_more_input, print_fn=output.append)

        self.assertEqual(output[-1], "Input ended, stopping the game.")

    def test_chinese_round_uses_chinese_messages(self):
        output = []

        game.play(1, 10, "zh", 4, input_fn=_feed("4"), print_fn=output.append)

        self.assertIn("请猜一个", output[0])
        self.assertIn("恭喜你", output[-1])


class DrawAnswerTests(unittest.TestCase):
    def test_returns_the_remote_value_without_a_notice(self):
        notices = []

        with patch.object(entropy, "draw", return_value=9) as draw:
            answer = game.draw_answer(
                "randomorg", 1, 10, "en", notify=notices.append, timeout=3.0
            )

        self.assertEqual(answer, 9)
        self.assertEqual(notices, [])
        self.assertEqual(draw.call_args[0][:3], ("randomorg", 1, 10))

    def test_passes_a_deadline_matching_the_timeout(self):
        seen = {}

        def fake_draw(source_key, minimum, maximum, deadline):
            seen["deadline"] = deadline
            return 5

        with patch.object(entropy, "draw", fake_draw):
            game.draw_answer("curby", 1, 10, "en", notify=lambda _m: None, timeout=2.0)

        self.assertGreater(seen["deadline"].remaining, 0)
        self.assertLessEqual(seen["deadline"].remaining, 2.0)

    def test_falls_back_to_local_randomness_and_says_so(self):
        notices = []

        with patch.object(entropy, "draw", side_effect=entropy.SourceUnavailable("qrng")):
            with patch.object(entropy, "random_in_range", return_value=3) as local:
                answer = game.draw_answer("qrng", 1, 10, "zh", notify=notices.append)

        self.assertEqual(answer, 3)
        local.assert_called_once_with(1, 10)
        self.assertEqual(len(notices), 1)
        self.assertIn("量子真空涨落", notices[0])
        self.assertIn("本地随机数", notices[0])

    def test_local_source_never_contacts_the_network(self):
        with patch.object(entropy.SOURCES["qrng"], "fetch") as qrng_fetch:
            game.draw_answer("local", 1, 10, "en", notify=lambda _m: None)

        qrng_fetch.assert_not_called()
