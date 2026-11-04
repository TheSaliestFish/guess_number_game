"""Localized user-facing strings for the game."""

MESSAGES = {
    "zh": {
        "intro": "猜数字游戏：请猜一个 {minimum} 到 {maximum} 之间的整数。",
        "prompt": "请输入你的猜测：",
        "invalid": "请输入有效的整数。",
        "low": "太小了，再试一次！",
        "high": "太大了，再试一次！",
        "won": "恭喜你，猜对了！你一共猜了 {attempts} 次。",
        "fallback": "「{source}」获取失败，已改用本地随机数。",
        "aborted": "输入已结束，游戏停止。",
    },
    "en": {
        "intro": "Guess the number: enter an integer between {minimum} and {maximum}.",
        "prompt": "Your guess: ",
        "invalid": "Please enter a valid integer.",
        "low": "Too low. Try again!",
        "high": "Too high. Try again!",
        "won": "Congratulations! You guessed it in {attempts} attempts.",
        "fallback": "{source} is unavailable, using local random numbers instead.",
        "aborted": "Input ended, stopping the game.",
    },
}

LANGUAGES = tuple(MESSAGES)


def text(language, key, **fields):
    """Return the message `key` for `language`, filled in with `fields`."""
    return MESSAGES[language][key].format(**fields)
