#!/usr/bin/env python3
"""Normalize any raw transcript into the standard timestamped Markdown file.

    python3 scripts/format_transcript.py INPUT -o out.md --title "..." \
            [--meta "视频链接: ..." --meta "频道: ..."] [--merge-seconds 20]
            [--format auto|json3|vtt|srt|panel|plain]

Input formats it understands:
  json3   YouTube caption JSON (`fmt=json3`)
  vtt/srt subtitle files
  panel   YouTube / Substack transcript panel text: a bare timestamp line
          (`0:00` or `00:01:23`), optionally a speaker name line, then text
  plain   no timestamps at all — kept as paragraphs

Output is always:
    # <title>
    - <meta line>
    ---
    **[mm:ss]** text        (or `**[mm:ss] 【Speaker】** text`)
"""
import argparse
import json
import os
import re
import sys

TS = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?:[.,]\d+)?\s*$")
CUE = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})[.,](\d{3})\s*-->")


def hms(sec):
    sec = int(sec)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _secs(h, m, s):
    return int(h or 0) * 3600 + int(m) * 60 + int(s)


def from_json3(data):
    out = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        txt = re.sub(r"\s+", " ", "".join(s.get("utf8", "") for s in segs)).strip()
        if txt:
            out.append((ev.get("tStartMs", 0) / 1000.0, None, txt))
    return out


def from_cues(text):
    """WebVTT / SRT."""
    out, cur, buf = [], None, []
    for line in text.splitlines():
        m = CUE.match(line)
        if m:
            if cur is not None and buf:
                out.append((cur, None, " ".join(buf)))
            cur, buf = _secs(m.group(1), m.group(2), m.group(3)), []
            continue
        s = re.sub(r"<[^>]+>", "", line).strip()
        if not s or s.isdigit() or s.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue
        if cur is not None:
            buf.append(s)
    if cur is not None and buf:
        out.append((cur, None, " ".join(buf)))
    dedup = []
    for t, sp, txt in out:
        if dedup:
            prev = dedup[-1][2]
            if txt == prev or prev.endswith(txt):
                continue
            if txt.startswith(prev + " "):
                txt = txt[len(prev) + 1:]
        dedup.append((t, sp, txt))
    return dedup


def from_panel(text, speakers=True):
    """Transcript panels: timestamp line, optional speaker line, then body text."""
    lines = [l.rstrip() for l in text.splitlines()]
    out, cur_t, cur_sp, buf = [], None, None, []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = TS.match(line)
        if m:
            if cur_t is not None and buf:
                out.append((cur_t, cur_sp, " ".join(buf)))
            cur_t, cur_sp, buf = _secs(m.group(1), m.group(2), m.group(3)), None, []
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            nxt = lines[j].strip() if j < len(lines) else ""
            if (speakers and nxt and len(nxt) < 40 and not TS.match(nxt)
                    and not nxt.endswith((".", "?", "!", "，", "。", ",", ":"))
                    and len(nxt.split()) <= 5 and nxt[:1].isupper()):
                cur_sp = nxt
                i = j + 1
                continue
            i += 1
            continue
        if line.strip():
            buf.append(line.strip())
        i += 1
    if cur_t is not None and buf:
        out.append((cur_t, cur_sp, " ".join(buf)))
    return out


def sniff(text, path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json" or text.lstrip().startswith("{"):
        return "json3"
    if ext == ".vtt" or text.lstrip().startswith("WEBVTT") or CUE.search(text):
        return "vtt"
    if ext == ".srt":
        return "srt"
    if sum(1 for l in text.splitlines()[:400] if TS.match(l)) >= 3:
        return "panel"
    return "plain"


def merge(blocks, window):
    """Group fragments into ~`window`-second paragraphs; never merge across speakers."""
    if window <= 0:
        return blocks
    out, start, sp, buf = [], None, None, []
    for t, s, txt in blocks:
        if start is not None and (t - start >= window or (s and s != sp)):
            out.append((start, sp, " ".join(buf)))
            start, sp, buf = None, None, []
        if start is None:
            start, sp = t, s
        buf.append(txt)
    if buf:
        out.append((start or 0, sp, " ".join(buf)))
    return [(t, s, re.sub(r"\s+([,.!?;:])", r"\1", re.sub(r"\s+", " ", b)).strip())
            for t, s, b in out]


def render(title, meta_lines, blocks, window=20):
    head = [f"# {title}", ""]
    head += [f"- {m}" for m in meta_lines]
    head += ["", "---", ""]
    body = []
    for t, sp, txt in merge(blocks, window):
        tag = f"**[{hms(t)}]{(' 【' + sp + '】') if sp else ''}**"
        body.append(f"{tag} {txt}")
    return "\n".join(head) + "\n\n".join(body) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", default="逐字稿（Transcript）")
    ap.add_argument("--meta", action="append", default=[])
    ap.add_argument("--merge-seconds", type=int, default=20)
    ap.add_argument("--format", default="auto",
                    choices=["auto", "json3", "vtt", "srt", "panel", "plain"])
    ap.add_argument("--no-speakers", action="store_true")
    a = ap.parse_args()

    text = open(a.input, encoding="utf-8", errors="replace").read()
    fmt = sniff(text, a.input) if a.format == "auto" else a.format
    if fmt == "json3":
        blocks = from_json3(json.loads(text))
    elif fmt in ("vtt", "srt"):
        blocks = from_cues(text)
    elif fmt == "panel":
        blocks = from_panel(text, speakers=not a.no_speakers)
    else:
        blocks = [(0, None, p.strip()) for p in re.split(r"\n{2,}", text) if p.strip()]

    if not blocks:
        print(json.dumps({"error": "no_blocks", "detected_format": fmt}))
        sys.exit(2)

    open(a.out, "w", encoding="utf-8").write(
        render(a.title, a.meta, blocks, a.merge_seconds))
    print(json.dumps({"file": a.out, "detected_format": fmt,
                      "raw_segments": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
