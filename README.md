# 猜数字游戏 | Guess the Number

一个轻量的命令行猜数字游戏。程序随机选择指定范围内的整数，提示猜测过高或过低，并统计有效猜测次数。支持中文和英文，无需运行时第三方依赖。

A small command-line number guessing game. Guess the randomly selected integer in a configurable range, get higher/lower hints, and see the number of valid attempts. Chinese and English are supported, with no runtime dependencies.

## 开始使用 | Getting started

需要 Python 3。两种等价入口 / Two equivalent entry points with Python 3:

```bash
python3 guess_number_game.py
python3 -m guess_number_game
```

默认范围是 1 到 100，默认使用中文。运行 `--help` 查看帮助。

The default range is 1–100 and the default language is Chinese. Run `--help` for help.

## 命令行选项 | Options

| 选项 / Option | 说明 / Description | 默认值 / Default |
| --- | --- | --- |
| `--min INTEGER` | 最小值（包含）/ Inclusive lower bound | `1` |
| `--max INTEGER` | 最大值（包含）/ Inclusive upper bound | `100` |
| `-l`, `--language {zh,en}` | 游戏语言 / Game language | `zh` |
| `-s`, `--source {qrng,randomorg,curby,local}` | 随机源 / Randomness source | `qrng` |
| `-h`, `--help` | 显示帮助 / Show help | — |

`--min` 必须小于 `--max`。例如，使用英文并猜测 10 到 20 之间的数字：

`--min` must be less than `--max`. For example, play in English with a range of 10 to 20:

```bash
python3 guess_number_game.py --min 10 --max 20 --language en
```

## 随机源 | Randomness sources

默认向 ANU QRNG 请求一次量子真空涨落随机数，可用 `--source` 切换：

The secret number is drawn once from ANU QRNG's quantum vacuum fluctuations by default; use `--source` to switch:

| `--source` | 随机源 / Source | 说明 / Notes |
| --- | --- | --- |
| `qrng` | ANU QRNG / 量子真空涨落 / quantum vacuum fluctuations | 返回 64 字节量子熵 / 64 bytes of quantum entropy |
| `randomorg` | Random.org / 大气噪声 / atmospheric noise | 整数接口直接返回区间内的值 / integer API returns a value in range |
| `curby` | CURBy / 贝尔测试量子随机信标 / Bell-test quantum beacon | 取最新一轮信标的 CID 摘要；信标按轮次更新，同一轮内多次运行会得到相同随机值 / uses the latest beacon round's CID digest, so repeats until the next round |
| `local` | 本地伪随机 / local PRNG | 不发起网络请求 / no network request |

每次启动只请求一次，**超时 2 秒**即放弃。请求超时或失败时会打印提示并改用本地随机数继续游戏，例如：

Each run makes a single request with a **2 second timeout**. On timeout or failure the game prints a notice and continues with local randomness, for example:

```text
「量子真空涨落（ANU QRNG）」获取失败，已改用本地随机数。
ANU QRNG (quantum vacuum fluctuations) is unavailable, using local random numbers instead.
```

## 项目结构 | Project structure

依赖方向单向：`cli → game → entropy → transport`。每个随机源是一个独立适配器，互不引用；游戏循环不认识网络，传输层不认识游戏。所有模块都不依赖第三方库。

Dependencies point one way: `cli → game → entropy → transport`. Each randomness source is a standalone adapter, the game loop knows nothing about HTTP, and the transport layer knows nothing about the game. No module needs third-party packages.

```text
guess_number_game/
├── __main__.py        # python -m guess_number_game 入口 / module entry point
├── cli.py             # 参数解析与组装 / argument parsing and wiring
├── game.py            # 游戏回合 + 兜底策略 / round loop and fallback policy
├── messages.py        # 中英文文案 / localized strings
├── transport.py       # 2 秒预算的 HTTP 客户端 / deadline-bound HTTP client
└── entropy/
    ├── base.py        # RandomSource 契约与异常 / source contract and errors
    ├── anu.py         # ANU QRNG 适配器 / quantum vacuum adapter
    ├── random_org.py  # Random.org 适配器 / atmospheric noise adapter
    ├── curby.py       # CURBy 信标适配器 / quantum beacon adapter
    ├── local.py       # 本地伪随机 / local PRNG
    ├── mapping.py     # 字节 → 区间（拒绝采样）/ unbiased range mapping
    └── cid.py         # CIDv1 摘要解析 / multihash digest parsing
guess_number_game.py   # 兼容入口，仅转发 CLI / compatibility shim
```

## 测试 | Tests

按模块拆分，路由/适配器/游戏循环各自独立覆盖：

Tests are split per module — CLI wiring, adapters, mapping and the game loop are covered independently:

```bash
python3 -m unittest discover -s tests -v
```

## Windows 可执行文件 | Windows executable

推送格式为 `v*` 的版本标签（例如 `v1.0.0`）会自动触发 GitHub Actions：在 Windows 上构建单文件 `guess-number-game.exe`，并将它、README 和 MIT 许可证附加到对应的 GitHub Release。运行 `.exe` 不需要安装 Python。

Pushing a version tag matching `v*` (for example, `v1.0.0`) triggers GitHub Actions to build a single-file `guess-number-game.exe` on Windows and attach it, this README, and the MIT license to the matching GitHub Release. Python is not required to run the `.exe`.

## 许可证 | License

本项目以 MIT License 开源，详见 [LICENSE](LICENSE)。

Released under the MIT License. See [LICENSE](LICENSE).

## 贡献者与署名 | Contributors and attribution

人类维护者与 AI 编程智能体共同开发，智能体通过提交的 `Co-authored-by` 尾注署名，不持有仓库权限。详见 [CONTRIBUTORS.md](CONTRIBUTORS.md)。

Built by a human maintainer together with AI coding agents; agents are credited via `Co-authored-by` trailers and hold no repository access. See [CONTRIBUTORS.md](CONTRIBUTORS.md).
