# 取稿手册

各来源怎么拿到干净的逐字稿，以及踩过的坑。

## YouTube

### 路径 A：youtube-video-info skill（首选）

它维护着登录态（`.userdata/youtube-video-info/.cookie` 和 `.auth_headers`），能拿元信息和字幕。拿到原始字幕后用 `scripts/format_transcript.py` 转成标准 Markdown。

### 路径 B：本 skill 的抓取脚本

```bash
python3 scripts/fetch_youtube_transcript.py <url-or-video-id> \
    -o transcript_<vid>.md [--lang en] [--merge-seconds 20] \
    [--cookie-file <path>] [--save-json3 raw.json]
```

脚本行为：
- 走 InnerTube `youtubei/v1/player` 的 WEB client，自动在 `user_skills/*/.userdata/*/.cookie` 里找登录 cookie。
- 手工字幕优先于自动字幕（ASR），选中哪一种会写进文件头。
- 沙箱代理不稳，内置 3 次重试。
- 退出码：`0` 成功 / `2` 该视频没有任何字幕轨 / `3` 被拦截（`LOGIN_REQUIRED: Sign in to confirm you're not a bot`）。

**退出码 3 的正确反应**：cookie 过期或缺失，去 `youtube-video-info` 刷新登录态。反复重试没有用，数据中心 IP 必然被拦。实在拿不到就退回浏览器：打开视频页 → Show transcript → 复制面板文本 → 存成 txt → `format_transcript.py --format panel`。

退出码 2 说明视频真没字幕，这时候只能下音频走 ASR，先跟用户确认值不值得。

### 自动字幕的质量问题

自动字幕没有标点断句、专有名词经常错（人名、产品名、公司名）。翻译时靠上下文纠正，纠正过的地方如果影响理解，在中文里保留正确写法即可，不必逐处说明。但**如果某句原话要作为 blockquote 引用，而它来自自动字幕且明显有错词，就不要引用它**，换一句可靠的。

## Substack / Lenny's Newsletter

1. 原 URL 后加 `?showTranscript=true`，用 `web_fetch` 抓。
2. 页面很大，`web_fetch` 会提示输出过大并把全文落盘到 `tool_outputs/web_fetch_call_*.txt`。这个文件是 JSON，正文在 `result` 字段里且被转义过：

```python
import json
raw = json.load(open("tool_outputs/web_fetch_call_xxx.txt"))
text = raw["result"] if isinstance(raw, dict) else raw
open("page.md", "w").write(text)
```

3. **不要用 `read` 全量读这个文件**，会被截断。直接用 Python 处理。
4. 手工定位 transcript 的头尾。自动检测经常失败（比如靠 `Audio playback` 或第一个 `0:00` 定位会返回 None）：先看前 40 行确认真正的起始行号，尾部切在导航/推荐文章开始的地方。
5. Substack 的 transcript 面板格式是"时间戳单独一行 → 说话人单独一行 → 正文"，中间有空行。`format_transcript.py --format panel` 认得这个结构，会自动带出说话人。

## 通用网页 / 其他平台

- 静态页优先 `web_fetch`；失败了用当前环境可用的网页抓取工具。
- B 站、抖音等平台优先使用当前环境的音视频转文字能力；没有时下载音轨后走 ASR。
- 飞书妙记等会议录制使用平台原生导出能力，不属于本 skill 范围。

## 逐字稿文件规范

文件名：`<source>_<who>_transcript.md`，例如 `lenny_tara_transcript.md`、`transcript_P06RgnUKX_I.md`。

头部固定这几项，缺一项就去补：

```markdown
# <标题> — 逐字稿（Transcript）

- 视频链接 / 来源: https://...
- 频道 / 播客: Lenny's Podcast
- 嘉宾: Tara Seshan — OpenAI 产品负责人（Codex & ChatGPT Work），此前 Stripe 前五号 PM
- 主持人: Lenny Rachitsky
- 时长: 1:21:44 | 发布日期: 2026-xx-xx
- 字幕来源: YouTube 官方人工字幕（en）/ 自动生成字幕 / 页面 transcript 面板

---
```

正文用 `**[mm:ss]** 文本` 或 `**[mm:ss] 【Speaker】** 文本`。

**这个文件要留在任务工作目录**，后面所有引用、时间戳核对、二次加工都靠它，不要抓完就扔。

## 中文全文逐字稿（用户明确要"翻译全文"时）

单独出一份 `*_zh.md`：
- 时间戳与英文版严格对齐，方便对照。
- 每隔几分钟按话题切一个 `### 00:00 小标题`，标题自己拟，概括这一段在讲什么。
- 说话人用 `【姓名】` 标出。
- 语气口语化，是"人在说话"不是"文档在陈述"。
