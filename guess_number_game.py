import argparse
import random


MESSAGES = {
    "zh": {
        "intro": "猜数字游戏：请猜一个 {minimum} 到 {maximum} 之间的整数。",
        "prompt": "请输入你的猜测：",
        "invalid": "请输入有效的整数。",
        "low": "太小了，再试一次！",
        "high": "太大了，再试一次！",
        "won": "恭喜你，猜对了！你一共猜了 {attempts} 次。",
    },
    "en": {
        "intro": "Guess the number: enter an integer between {minimum} and {maximum}.",
        "prompt": "Your guess: ",
        "invalid": "Please enter a valid integer.",
        "low": "Too low. Try again!",
        "high": "Too high. Try again!",
        "won": "Congratulations! You guessed it in {attempts} attempts.",
    },
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Play a number guessing game in Chinese or English."
    )
    parser.add_argument("--min", dest="minimum", type=int, default=1, help="minimum number (default: 1)")
    parser.add_argument("--max", dest="maximum", type=int, default=100, help="maximum number (default: 100)")
    parser.add_argument(
        "-l",
        "--language",
        choices=("zh", "en"),
        default="zh",
        help="game language: zh or en (default: zh)",
    )
    return parser


def play(minimum, maximum, language, input_fn=input, print_fn=print):
    messages = MESSAGES[language]
    answer = random.randint(minimum, maximum)
    attempts = 0

    print_fn(messages["intro"].format(minimum=minimum, maximum=maximum))
    while True:
        try:
            guess = int(input_fn(messages["prompt"]))
        except ValueError:
            print_fn(messages["invalid"])
            continue

        attempts += 1
        if guess < answer:
            print_fn(messages["low"])
        elif guess > answer:
            print_fn(messages["high"])
        else:
            print_fn(messages["won"].format(attempts=attempts))
            return


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.minimum >= args.maximum:
        parser.error("--min must be less than --max")
    play(args.minimum, args.maximum, args.language)


if __name__ == "__main__":
    main()
