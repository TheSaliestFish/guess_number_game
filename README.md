# 猜数字游戏 | Guess the Number

一个轻量的命令行猜数字游戏。程序随机选择指定范围内的整数，提示猜测过高或过低，并统计有效猜测次数。支持中文和英文，无需运行时第三方依赖。

A small command-line number guessing game. Guess the randomly selected integer in a configurable range, get higher/lower hints, and see the number of valid attempts. Chinese and English are supported, with no runtime dependencies.

## 开始使用 | Getting started

需要 Python 3. Run with Python 3:

```bash
python3 guess_number_game.py
```

默认范围是 1 到 100，默认使用中文。运行 `python3 guess_number_game.py --help` 查看帮助。

The default range is 1–100 and the default language is Chinese. Run `python3 guess_number_game.py --help` for help.

## 命令行选项 | Options

| 选项 / Option | 说明 / Description | 默认值 / Default |
| --- | --- | --- |
| `--min INTEGER` | 最小值（包含）/ Inclusive lower bound | `1` |
| `--max INTEGER` | 最大值（包含）/ Inclusive upper bound | `100` |
| `-l`, `--language {zh,en}` | 游戏语言 / Game language | `zh` |
| `-h`, `--help` | 显示帮助 / Show help | — |

`--min` 必须小于 `--max`。例如，使用英文并猜测 10 到 20 之间的数字：

`--min` must be less than `--max`. For example, play in English with a range of 10 to 20:

```bash
python3 guess_number_game.py --min 10 --max 20 --language en
```

## 测试 | Tests

```bash
python3 -m unittest discover -s tests -v
```

## Windows 可执行文件 | Windows executable

推送格式为 `v*` 的版本标签（例如 `v1.0.0`）会自动触发 GitHub Actions：在 Windows 上构建单文件 `guess-number-game.exe`，并将它、README 和 MIT 许可证附加到对应的 GitHub Release。运行 `.exe` 不需要安装 Python。

Pushing a version tag matching `v*` (for example, `v1.0.0`) triggers GitHub Actions to build a single-file `guess-number-game.exe` on Windows and attach it, this README, and the MIT license to the matching GitHub Release. Python is not required to run the `.exe`.

## 许可证 | License

本项目以 MIT License 开源，详见 [LICENSE](LICENSE)。

Released under the MIT License. See [LICENSE](LICENSE).
