import unittest

from guess_number_game import messages


class MessagesTests(unittest.TestCase):
    def test_all_languages_expose_the_same_keys(self):
        expected = set(messages.MESSAGES["zh"])

        for language in messages.LANGUAGES:
            self.assertEqual(set(messages.MESSAGES[language]), expected, language)

    def test_text_fills_in_placeholders(self):
        self.assertIn("10", messages.text("zh", "intro", minimum=1, maximum=10))
        self.assertIn("10", messages.text("en", "intro", minimum=1, maximum=10))

    def test_fallback_message_names_the_source(self):
        rendered = messages.text("zh", "fallback", source="Random.org 大气噪声")

        self.assertIn("Random.org 大气噪声", rendered)
        self.assertIn("本地随机数", rendered)
