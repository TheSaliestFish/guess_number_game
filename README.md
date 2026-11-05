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
| `-s`, `--source {beacon,trng,vrf}` | 随机源大类 / Randomness family | `trng` |
| `--version` | 显示版本 / Show version | — |
| `-h`, `--help` | 显示帮助 / Show help | — |

`--min` 必须小于 `--max`。例如，使用英文并猜测 10 到 20 之间的数字：

`--min` must be less than `--max`. For example, play in English with a range of 10 to 20:

```bash
python3 guess_number_game.py --min 10 --max 20 --language en
```

## 随机源 | Randomness sources

`--source` 只选**大类**，大类内部的所有服务会被**同时**请求，谁先给出结果就用谁的结果：

`--source` picks a **family**; every service inside it is queried **concurrently** and the first answer wins:

| `--source` | 大类 / Family | 并发请求的服务 / Sources queried in parallel |
| --- | --- | --- |
| `beacon` | 可验证随机信标 / verifiable randomness beacons | NIST Randomness Beacon（512 位、带签名与时间戳）、drand / League of Entropy（阈值 BLS）、CURBy（贝尔测试信标，取最新一轮 CID 摘要） |
| `trng` | 真随机 / 量子随机 API | Random.org（大气噪声）、ANU QRNG（量子真空涨落）、CSRNG Lite（NIST 认证 RNG） |
| `vrf` | Web3 可验证随机函数 | Chainlink VRF（链上结果，需配置 RPC 与合约） |

**超时规则**：所有请求发出后开始计时，**最后一个请求发出后 2 秒**仍无任何结果即判定超时；若全部源立即失败则不空等，马上回退。超时或全部失败时打印提示并用本地随机数继续游戏，例如：

**Timeout rule**: the clock starts once the last request has been dispatched — **two seconds after the final request** without an answer means timeout. If every source fails immediately the game falls back without waiting out the window. On timeout or total failure it prints a notice and continues with local randomness, for example:

```text
「真随机 / 量子随机 API（Random.org / ANU QRNG / CSRNG）」获取失败，已改用本地随机数。
true and quantum randomness APIs (Random.org / ANU QRNG / CSRNG) is unavailable, using local random numbers instead.
```

### Chainlink VRF 配置 | Chainlink VRF configuration

Chainlink VRF 是链上接口，没有公开 REST 端点。配置下面三个环境变量后，游戏会用 JSON-RPC `eth_call` 读取你已实现的 VRF 消费者合约中的随机字；未配置时该源直接判为不可用并回退。

Chainlink VRF is on-chain and has no public REST endpoint. With these environment variables the game reads a fulfilled random word from your VRF consumer contract through a JSON-RPC `eth_call`; without them the source is treated as unavailable.

```bash
export GUESSGAME_VRF_RPC="https://your-rpc.example"   # JSON-RPC 节点 / node
export GUESSGAME_VRF_TO="0xYourConsumerContract"      # 消费者合约 / consumer contract
export GUESSGAME_VRF_DATA="0x..."                     # 读取随机字的 calldata / calldata
```

## 项目结构 | Project structure

依赖方向单向：`cli → game → entropy → transport`。每个随机源是一个独立适配器，互不引用；同一个大类内由 `entropy/fanout.py` 并发发起请求、取最先返回的结果；游戏循环不认识网络，传输层不认识游戏。所有模块都不依赖第三方库。

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
    ├── fanout.py      # 并发请求一个类别的全部源 / parallel fan-out
    ├── nist.py        # NIST 随机信标 / NIST beacon
    ├── drand.py       # drand / League of Entropy
    ├── curby.py       # CURBy 信标 / Bell-test beacon
    ├── random_org.py  # Random.org 大气噪声 / atmospheric noise
    ├── anu.py         # ANU QRNG 量子真空涨落 / quantum vacuum
    ├── csrng.py       # CSRNG Lite
    ├── chainlink_vrf.py  # Chainlink VRF（链上）/ on-chain VRF
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
