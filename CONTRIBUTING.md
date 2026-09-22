# Contributing

感谢你愿意改进 `youtube-transcript-digest`。这是一个以内容质量为核心的 Skill：代码能跑只是起点，输出是否可回查、是否区分证据强弱同样重要。

## 提交 Issue

请尽量包含：

- 输入来源与链接类型（YouTube、Substack、VTT、SRT 等）；
- 预期行为与实际行为；
- 可复现步骤；
- 脚本退出码和错误信息（请删除 cookie、token 等敏感内容）；
- 如果是内容质量问题，请给出具体段落、时间戳或置信度误判。

## 提交 Pull Request

1. Fork 仓库并创建语义清楚的分支；
2. 保持改动聚焦，一个 PR 解决一个问题；
3. 不要提交 cookie、登录态、原始私密转录稿或 `__pycache__`；
4. 更新相关 README / reference，说明行为变化；
5. 在本地完成基础检查。

```bash
python3 -m py_compile scripts/fetch_youtube_transcript.py scripts/format_transcript.py
python3 scripts/format_transcript.py --help
python3 scripts/fetch_youtube_transcript.py --help
```

## 内容规则变更

修改 `SKILL.md` 或 `references/` 时，请同时检查：

- 是否仍然区分事实、嘉宾自述与整理者推断；
- 是否保留引用的英文原文、中文翻译和时间戳；
- 是否改变了三档置信度定义；
- 新规则能否被外部用户复现，而不是依赖私人文档或本地 Prompt；
- 示例中是否含有不必要的个人信息、登录凭证或内部链接。

## 代码风格

- 优先使用 Python 标准库，新增依赖需说明原因；
- 错误信息应告诉调用方下一步怎么做；
- 对平台拦截、无字幕等可预期状态使用稳定退出码；
- 新增输入格式时，至少提供一个最小测试样例；
- 不在代码中写入 cookie、token 或账户信息。

## Commit 建议

使用清晰、可扫描的提交信息：

```text
feat: add transcript source adapter
fix: deduplicate rolling ASR captions
docs: clarify confidence audit boundary
```

提交 PR 即表示你同意项目维护者在本仓库中分发你的贡献。项目当前尚未声明开源许可证；如你的组织对贡献授权有额外要求，请先在 Issue 中沟通。
