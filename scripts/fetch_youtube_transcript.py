#!/usr/bin/env python3
"""Fetch a YouTube transcript + video metadata, write standard timestamped Markdown.

    python3 scripts/fetch_youtube_transcript.py <url-or-id> [-o out.md] [--lang en]
            [--cookie-file PATH] [--merge-seconds 20] [--save-json3 raw.json]

YouTube blocks datacenter IPs with "Sign in to confirm you're not a bot", so a
logged-in cookie is required. The script auto-discovers the cookie that the
`youtube-video-info` skill stores under its `.userdata/`; pass --cookie-file to
override. On LOGIN_REQUIRED it exits 3 with a JSON error so the caller knows to
refresh that cookie instead of retrying blindly.

Exit codes: 0 ok | 2 no caption track | 3 login required / blocked
"""
import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.parse

import requests

API = "https://www.youtube.com/youtubei/v1/player"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def parse_video_id(s):
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    u = urllib.parse.urlparse(s)
    if u.netloc.endswith("youtu.be"):
        return u.path.strip("/").split("/")[0]
    qs = urllib.parse.parse_qs(u.query)
    if "v" in qs:
        return qs["v"][0]
    m = re.search(r"/(?:embed|shorts|live)/([\w-]{11})", u.path)
    if m:
        return m.group(1)
    raise SystemExit(f"cannot parse video id from: {s}")


def discover_cookie(explicit):
    """Return (cookie, authorization) — reuse youtube-video-info's stored session."""
    paths = [explicit] if explicit else []
    ws = os.environ.get("AIME_WORKSPACE_PATH", ".")
    paths += sorted(glob.glob(os.path.join(ws, "user_skills/*/.userdata/*/.cookie")))
    for p in paths:
        if p and os.path.exists(p):
            cookie = open(p, encoding="utf-8").read().strip()
            auth = None
            ap = os.path.join(os.path.dirname(p), ".auth_headers")
            if os.path.exists(ap):
                m = re.search(r"AUTHORIZATION=(.*)", open(ap, encoding="utf-8").read())
                if m:
                    auth = m.group(1).strip()
            return cookie, auth
    return None, None


def player_response(video_id, cookie, auth, tries=3):
    h = {"content-type": "application/json", "user-agent": UA,
         "origin": "https://www.youtube.com",
         "referer": f"https://www.youtube.com/watch?v={video_id}"}
    if cookie:
        h["cookie"] = cookie
    if auth:
        h["authorization"] = auth
    body = {"context": {"client": {"clientName": "WEB",
                                   "clientVersion": "2.20240814.00.00",
                                   "hl": "en", "gl": "US"}},
            "videoId": video_id}
    err = None
    for i in range(tries):
        try:
            r = requests.post(API, headers=h, json=body, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 * (i + 1))
    raise SystemExit(f"player API failed after {tries} tries: {err}")


def pick_track(data, lang):
    tracks = (data.get("captions", {})
                  .get("playerCaptionsTracklistRenderer", {})
                  .get("captionTracks", []))
    def name(t):
        n = t.get("name", {})
        return n.get("simpleText") or "".join(r.get("text", "") for r in n.get("runs", []))
    catalog = [{"lang": t.get("languageCode"), "name": name(t),
                "kind": t.get("kind") or "manual"} for t in tracks]
    if not tracks:
        return None, catalog
    manual = [t for t in tracks if t.get("languageCode") == lang and t.get("kind") != "asr"]
    same = [t for t in tracks if t.get("languageCode") == lang]
    return (manual or same or tracks)[0], catalog


def fetch_json3(track, cookie):
    url = track["baseUrl"] + ("&" if "?" in track["baseUrl"] else "?") + "fmt=json3"
    h = {"user-agent": UA}
    if cookie:
        h["cookie"] = cookie
    r = requests.get(url, headers=h, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--out")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--cookie-file")
    ap.add_argument("--merge-seconds", type=int, default=20)
    ap.add_argument("--save-json3")
    a = ap.parse_args()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from format_transcript import from_json3, hms, render  # noqa: E402

    vid = parse_video_id(a.video)
    cookie, auth = discover_cookie(a.cookie_file)
    data = player_response(vid, cookie, auth)

    status = data.get("playabilityStatus", {})
    if status.get("status") not in (None, "OK"):
        print(json.dumps({"error": "blocked", "status": status.get("status"),
                          "reason": status.get("reason"),
                          "hint": "cookie missing or expired — refresh the login cookie "
                                  "used by the youtube-video-info skill, or fall back to "
                                  "the transcript panel on the page"}, ensure_ascii=False))
        sys.exit(3)

    track, catalog = pick_track(data, a.lang)
    if not track:
        print(json.dumps({"error": "no_caption_track", "available": catalog},
                         ensure_ascii=False))
        sys.exit(2)

    raw = fetch_json3(track, cookie)
    if a.save_json3:
        json.dump(raw, open(a.save_json3, "w", encoding="utf-8"), ensure_ascii=False)

    d = data.get("videoDetails", {})
    mf = data.get("microformat", {}).get("playerMicroformatRenderer", {})
    kind = "自动生成" if track.get("kind") == "asr" else "官方/人工"
    dur = int(d.get("lengthSeconds") or 0)
    meta = [f"视频链接: https://www.youtube.com/watch?v={vid}",
            f"频道: {d.get('author', '')}",
            f"时长: {hms(dur)} | 发布日期: {mf.get('publishDate', '')}"
            f" | 观看: {int(d.get('viewCount') or 0):,}",
            f"字幕来源: YouTube {kind}字幕（{track.get('languageCode')}）"]
    md = render(f"{d.get('title', vid)} — 逐字稿（Transcript）", meta,
                from_json3(raw), a.merge_seconds)

    out = a.out or f"transcript_{vid}.md"
    open(out, "w", encoding="utf-8").write(md)
    print(json.dumps({"file": out, "video_id": vid, "title": d.get("title"),
                      "caption_kind": kind, "available_tracks": catalog},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
