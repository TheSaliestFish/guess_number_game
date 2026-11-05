# 贡献者 | Contributors

本项目由人类维护者与 AI 编程智能体协作完成。智能体通过提交里的 `Co-authored-by` 尾注署名（即 GitHub 贡献者列表里 Copilot 那种“隐性标记”），**不授予仓库写权限**。

This project is built by a human maintainer together with AI coding agents. Agents are credited through `Co-authored-by` trailers in commits — the same hidden marker that makes Copilot show up in the contributor graph — and **never receive repository access**.

| 贡献者 / Contributor | 角色 / Role | 署名身份 / Commit identity |
| --- | --- | --- |
| [@TheSaliestFish](https://github.com/TheSaliestFish) | 维护者 / maintainer | `TheSaliestFish <129015664+TheSaliestFish@users.noreply.github.com>` |
| DeepSeek Harness（DSH） | 编码智能体 / coding agent | `DeepSeek Harness <noreply@deepseek.com>` |
| Claude Code | 编码智能体 / coding agent | `Claude Code <noreply@anthropic.com>` |
| GitHub Copilot | 云端编码智能体 / cloud coding agent | `copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>` |

## 写法 | Trailer format

提交正文末尾留一个空行，再逐行写尾注：

Leave one blank line at the end of the commit message, then add the trailers:

```text
Add something useful

Co-authored-by: DeepSeek Harness <noreply@deepseek.com>
Co-authored-by: Claude Code <noreply@anthropic.com>
```

只有实际参与该次改动的智能体才出现在尾注里；一次提交可以同时有多个尾注。
Only the agents that actually touched that change are listed; one commit may carry several trailers.
