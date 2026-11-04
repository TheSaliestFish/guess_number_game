import argparse
import base64
import http.client
import json
import random
import time
import urllib.request


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

# Total time budget for one remote randomness lookup, in seconds.
FALLBACK_TIMEOUT_SECONDS = 2.0

SOURCES = ("qrng", "randomorg", "curby", "local")

SOURCE_LABELS = {
    "qrng": {
        "zh": "量子真空涨落（ANU QRNG）",
        "en": "ANU QRNG (quantum vacuum fluctuations)",
    },
    "randomorg": {
        "zh": "Random.org 大气噪声",
        "en": "Random.org atmospheric noise",
    },
    "curby": {
        "zh": "CURBy 贝尔测试量子随机信标",
        "en": "CURBy Bell-test quantum random beacon",
    },
}

CURBY_API_URL = "https://api.entwine.me"
# CURBy-RNG chain on the CURBy twine spool (listed by GET /chains).
CURBY_CHAIN_CID = (
    "bafyriqci6f3st2mg7gq733ho4zvvth32zpy2mtiylixwmhoz6d627eo3jfpmbxepe"
    "54u2zdvymonq5sp3armtm4rodxsynsirr5g3xsbd3q4s"
)
QRNG_URL = "https://qrng.anu.edu.au/API/jsonI.php?length=64&type=uint8"


def _read_varint(data, offset):
    """Read one unsigned LEB128 varint, returning (value, next offset)."""
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7


def _cid_digest(cid):
    """Return the multihash digest of a base32 CIDv1; that digest is the CURBy randomness."""
    if not cid.startswith("b"):
        raise ValueError("unsupported CID multibase")
    payload = cid[1:].upper()
    payload += "=" * (-len(payload) % 8)
    raw = base64.b32decode(payload)
    version, offset = _read_varint(raw, 0)
    if version != 1:
        raise ValueError("unsupported CID version")
    _, offset = _read_varint(raw, offset)  # multicodec
    _, offset = _read_varint(raw, offset)  # multihash function code
    length, offset = _read_varint(raw, offset)
    digest = raw[offset:offset + length]
    if length == 0 or len(digest) != length:
        raise ValueError("malformed multihash digest")
    return digest


def _pick_from_bytes(data, minimum, maximum):
    """Map uniformly random bytes onto [minimum, maximum] with rejection sampling."""
    span = maximum - minimum + 1
    if span <= 1:
        return minimum
    bits = len(data) * 8
    limit = (1 << bits) - ((1 << bits) % span)
    value = int.from_bytes(data, "big")
    if value >= limit:
        raise ValueError("random value falls outside the usable range")
    return minimum + value % span


def _get(url, deadline, headers=None):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("randomness request timed out")
    request = urllib.request.Request(
        url, headers={"User-Agent": "guess-number-game/1.1", **(headers or {})}
    )
    with urllib.request.urlopen(request, timeout=remaining) as response:
        return response.read().decode("utf-8")


def _get_json(url, deadline, headers=None):
    return json.loads(_get(url, deadline, headers))


def _fetch_qrng(minimum, maximum, deadline):
    payload = _get_json(QRNG_URL, deadline)
    data = payload.get("data")
    if not payload.get("success", True) or not data:
        raise ValueError("ANU QRNG returned no random data")
    return _pick_from_bytes(bytes(data), minimum, maximum)


def _fetch_random_org(minimum, maximum, deadline):
    url = (
        "https://www.random.org/integers/?num=1&min={minimum}&max={maximum}"
        "&col=1&base=10&format=plain&rnd=new"
    ).format(minimum=minimum, maximum=maximum)
    value = int(_get(url, deadline).strip())
    if not minimum <= value <= maximum:
        raise ValueError("Random.org returned an out-of-range value")
    return value


def _fetch_curby(minimum, maximum, deadline):
    pulse = _get_json(
        "{base}/chains/{chain}/pulses/latest".format(
            base=CURBY_API_URL, chain=CURBY_CHAIN_CID
        ),
        deadline,
    )
    return _pick_from_bytes(_cid_digest(pulse["cid"]["/"]), minimum, maximum)


SOURCE_FETCHERS = {
    "qrng": _fetch_qrng,
    "randomorg": _fetch_random_org,
    "curby": _fetch_curby,
}


def choose_answer(
    minimum,
    maximum,
    source,
    language,
    print_fn=print,
    timeout=FALLBACK_TIMEOUT_SECONDS,
):
    """Pick the secret number from a remote entropy source, falling back to local randomness."""
    if source == "local":
        return random.randint(minimum, maximum)
    fetcher = SOURCE_FETCHERS.get(source)
    if fetcher is None:
        raise ValueError("unknown randomness source: {source}".format(source=source))
    deadline = time.monotonic() + timeout
    try:
        return fetcher(minimum, maximum, deadline)
    except (OSError, ValueError, TypeError, IndexError, http.client.HTTPException):
        print_fn(
            MESSAGES[language]["fallback"].format(source=SOURCE_LABELS[source][language])
        )
        return random.randint(minimum, maximum)


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
    parser.add_argument(
        "-s",
        "--source",
        choices=SOURCES,
        default="qrng",
        help=(
            "randomness source: qrng (ANU quantum vacuum), randomorg (atmospheric noise), "
            "curby (CURBy quantum beacon), local (default: qrng)"
        ),
    )
    return parser


def play(minimum, maximum, language, input_fn=input, print_fn=print, source="local"):
    """Run one game. `source` defaults to local randomness so callers opt into the network."""
    messages = MESSAGES[language]
    answer = choose_answer(minimum, maximum, source, language, print_fn=print_fn)
    attempts = 0

    print_fn(messages["intro"].format(minimum=minimum, maximum=maximum))
    while True:
        try:
            guess = int(input_fn(messages["prompt"]))
        except ValueError:
            print_fn(messages["invalid"])
            continue
        except EOFError:
            print_fn(messages["aborted"])
            return

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
    play(args.minimum, args.maximum, args.language, source=args.source)


if __name__ == "__main__":
    main()
