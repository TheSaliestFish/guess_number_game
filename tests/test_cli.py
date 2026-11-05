import unittest
from unittest.mock import patch

from guess_number_game import __version__, cli, entropy


class ParserTests(unittest.TestCase):
    def test_defaults(self):
        args = cli.build_parser().parse_args([])

        self.assertEqual((args.minimum, args.maximum), (1, 100))
        self.assertEqual((args.language, args.source), ("zh", "trng"))

    def test_source_choices_are_the_three_families(self):
        parser = cli.build_parser()

        self.assertEqual(tuple(entropy.GROUP_KEYS), ("beacon", "trng", "vrf"))
        self.assertEqual(parser.parse_args(["-s", "beacon"]).source, "beacon")
        with self.assertRaises(SystemExit):
            parser.parse_args(["--source", "randomorg"])

    def test_invalid_range_is_rejected(self):
        with self.assertRaises(SystemExit) as error:
            cli.main(["--min", "5", "--max", "5"])

        self.assertEqual(error.exception.code, 2)

    def test_version_flag_reports_the_package_version(self):
        with self.assertRaises(SystemExit) as error:
            cli.build_parser().parse_args(["--version"])

        self.assertEqual(error.exception.code, 0)
        self.assertEqual(__version__, "1.2.0")


class WiringTests(unittest.TestCase):
    def test_main_draws_the_answer_and_starts_the_round(self):
        with patch.object(cli, "draw_answer", return_value=7) as draw_answer:
            with patch.object(cli, "play") as play:
                cli.main(["--min", "1", "--max", "10", "-l", "en", "-s", "beacon"])

        draw_answer.assert_called_once_with("beacon", 1, 10, "en")
        play.assert_called_once_with(1, 10, "en", 7)
