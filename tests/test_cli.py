import unittest
from unittest.mock import patch

from guess_number_game import cli


class ParserTests(unittest.TestCase):
    def test_defaults(self):
        args = cli.build_parser().parse_args([])

        self.assertEqual((args.minimum, args.maximum), (1, 100))
        self.assertEqual((args.language, args.source), ("zh", "qrng"))

    def test_source_choices(self):
        parser = cli.build_parser()

        self.assertEqual(parser.parse_args(["-s", "curby"]).source, "curby")
        with self.assertRaises(SystemExit):
            parser.parse_args(["--source", "nope"])

    def test_invalid_range_is_rejected(self):
        with self.assertRaises(SystemExit) as error:
            cli.main(["--min", "5", "--max", "5"])

        self.assertEqual(error.exception.code, 2)


class WiringTests(unittest.TestCase):
    def test_main_draws_the_answer_and_starts_the_round(self):
        with patch.object(cli, "draw_answer", return_value=7) as draw_answer:
            with patch.object(cli, "play") as play:
                cli.main(["--min", "1", "--max", "10", "-l", "en", "-s", "randomorg"])

        draw_answer.assert_called_once_with("randomorg", 1, 10, "en")
        play.assert_called_once_with(1, 10, "en", 7)
