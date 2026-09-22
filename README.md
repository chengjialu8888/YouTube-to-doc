<div align="center">
  <img src="assets/banner.jpg" alt="youtube-transcript-digest — from video to evidence-aware insight document" width="100%" />

  <h1>youtube-transcript-digest</h1>

  <p><strong>English</strong> · <a href="README.zh-CN.md">简体中文</a></p>

  <p><strong>Turn long-form video and podcast transcripts into evidence-aware Chinese insight documents.</strong></p>
  <p>Not another transcript summarizer—a complete workflow from extraction and restructuring to evidence auditing and Lark delivery.</p>

  <p>
    <a href="SKILL.md"><img alt="AIME Skill" src="https://img.shields.io/badge/AIME-Skill-4C6FFF?style=flat-square"></a>
    <a href="https://www.python.org/"><img alt="Python 3" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white"></a>
    <a href="https://github.com/chengjialu8888/YouTube-to-doc/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/chengjialu8888/YouTube-to-doc?style=flat-square"></a>
    <a href="https://github.com/chengjialu8888/YouTube-to-doc/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/chengjialu8888/YouTube-to-doc?style=flat-square"></a>
  </p>

  <p>
    <a href="#why-this-skill-exists">Why</a> ·
    <a href="#what-it-does">Features</a> ·
    <a href="#quick-start">Quick start</a> ·
    <a href="#workflow">Workflow</a> ·
    <a href="#project-structure">Structure</a>
  </p>
</div>

---

## Why this Skill exists

The hardest part of working with long-form video is not obtaining a transcript. It is turning that transcript into something you can actually use:

- Literal translation preserves the original order—and all of its repetition and looseness.
- Facts, first-person claims, inference, and marketing language are mixed together.
- Summaries often omit the original quote, timestamp, and evidentiary boundary.
- A document may look complete while leaving readers unsure which conclusions are safe to carry forward.

`youtube-transcript-digest` solves the problem in two layers:

1. **Restructure** — reorganize the conversation around arguments, with each section resolving one question.
2. **Audit** — examine incentives, external evidence, and meaningful omissions, then grade every section by confidence.

The result is not merely a shorter transcript. It is a Chinese insight document that is **quotable, traceable, and decision-ready**.

## What it does

| Capability | Output |
|---|---|
| Transcript retrieval | Collect transcripts from YouTube, Substack / Lenny’s Newsletter, or existing subtitle files |
| Format normalization | Parse JSON3, VTT, SRT, transcript panels, and plain text |
| Chinese translation and restructuring | Follow a user-provided outline or the conversation’s own logic instead of translating mechanically |
| Confidence audit | Separate high-confidence facts, plausible first-party information, and marketing claims |
| Traceable quotations | Preserve the English quote, Chinese translation, speaker, and timestamp |
| Lark document delivery | Produce anchored TL;DRs, judgment-led headings, editable whiteboards, and takeaway lists |
| Follow-up material | Translate strongly recommended articles, papers, or checklists into separate documents |
| Chinese language QA | Apply an embedded “judgment → evidence → boundary” writing standard to remove generic AI prose |

### Input-to-output routing

| What you ask for | Default deliverable |
|---|---|
| “Get the transcript” | Local Markdown with metadata and timestamps |
| “Translate the full transcript” | English source transcript plus a Chinese transcript |
| “Extract the key insights” | Restructured Chinese insight document in Lark |
| “Organize it using this outline” | Insight document following the outline in the original order |
| “Summarize this” | Shorter Lark summary without a full translation |

## Quick start

### 1. Install as an AIME Skill

Clone the repository into your user Skill directory:

```bash
git clone https://github.com/chengjialu8888/YouTube-to-doc.git \
  user_skills/youtube-transcript-digest
```

You can also download the repository as a ZIP and import it as a user Skill in AIME. The Skill entry point is [`SKILL.md`](SKILL.md).

### 2. Install the script dependency

```bash
python3 -m pip install requests
```

### 3. Invoke it in natural language

```text
Get the transcript for this YouTube video: <URL>
```

```text
Use youtube-transcript-digest to turn this interview into a Chinese insight document.
Focus on product judgments, key decisions, counterintuitive ideas, and actionable advice.
```

```text
Translate and organize the interview using this outline:
1. ...
2. ...
3. ...
```

### 4. Use the transcript utilities directly

Fetch a YouTube transcript and write normalized Markdown:

```bash
python3 scripts/fetch_youtube_transcript.py '<youtube-url-or-id>' \
  --lang en \
  -o transcript.md
```

Normalize an existing subtitle file:

```bash
python3 scripts/format_transcript.py raw.vtt \
  --title 'Title — Transcript' \
  --meta 'Source: https://...' \
  --meta 'Caption source: official human-authored captions' \
  -o transcript.md
```

The formatter supports `json3`, `vtt`, `srt`, `panel`, and `plain`. It detects the format, merges fragments, removes rolling ASR duplication, and identifies speakers where possible.

> [!NOTE]
> YouTube may block requests from datacenter IPs. If the fetcher exits with code `3`, refresh the authenticated cookie or use the page’s transcript panel. Blind retries will not help.

## Workflow

```text
Video / podcast URL
        ↓
Retrieve transcript and metadata
        ↓
Normalize timestamps, speakers, and source labels
        ↓
Inspect incentives, external evidence, and omissions
        ↓
Restructure by outline or narrative logic
        ↓
Assign confidence at section level
        ↓
Run language QA + create editable Lark whiteboards
        ↓
Lark insight document / Markdown transcript
```

### Confidence is not decoration

| Level | Standard | Recommended use |
|---|---|---|
| ✅ **High confidence** | Confirmed by first-hand testing, official material, or multiple independent sources | Safe to cite as fact |
| 💡 **New and plausible** | Available only from the speaker, but internally coherent and consistent with the public timeline | Useful as product-history material, not as independently verified fact |
| ❗ **Marketing claim** | Conflicts with external evidence or relies on unfalsifiable self-assessment | Flag the conflict explicitly; do not quote it as fact |

See [`references/confidence-audit.md`](references/confidence-audit.md) for the full methodology.

### Default document blueprint

A standard Lark deliverable includes:

1. A one-image overview;
2. Five primary judgments;
3. Source context, incentives, and the confidence framework;
4. A TL;DR with anchors into the body;
5. Judgment-led chapter titles in the form `Topic: conclusion`;
6. A confidence note at the end of each chapter;
7. `Summary: N ideas worth taking away`.

See [`references/lark-doc-blueprint.md`](references/lark-doc-blueprint.md) for the complete structure.

## Design principles

- **Lead with the judgment.** A heading should make a claim, not merely label a topic.
- **Keep evidence traceable.** Important quotations retain the English source, Chinese translation, and timestamp.
- **Separate fact from inference.** Editor inference is marked with `〔推断〕`.
- **Audit before writing.** Evidence strength determines the tone of each section.
- **Do not silently discard material.** Important content outside the outline belongs in a separate section.
- **Review visuals online.** Export every Lark whiteboard preview before delivery.
- **Make the method portable.** Core language and audit standards ship with the repository rather than depending on private prompts.

## Project structure

```text
.
├── README.md                          # English project homepage
├── README.zh-CN.md                    # Chinese documentation
├── SKILL.md                           # Skill entry point and execution workflow
├── assets/
│   └── banner.jpg                     # README hero banner
├── references/
│   ├── confidence-audit.md            # Three-level confidence audit
│   ├── fetching-transcripts.md        # YouTube / Substack retrieval guide
│   ├── lark-doc-blueprint.md          # Lark document structure and XML conventions
│   └── translation-style.md           # Chinese translation and language QA rules
└── scripts/
    ├── fetch_youtube_transcript.py    # YouTube transcript and metadata retrieval
    └── format_transcript.py           # Multi-format transcript normalization
```

## Boundaries and known limitations

- The project does not bypass paywalls, DRM, or platform access controls.
- Videos without caption tracks require a separate ASR step; the current fetcher does not download and transcribe audio automatically.
- Proper nouns in automatic captions may be wrong; verify important quotations manually.
- Lark documents and editable whiteboards require corresponding Lark / Feishu tools in the runtime environment.
- Confidence grades are evidence-management labels, not judgments about a guest’s character or a product’s overall value.

## Contributing

Issues and pull requests are welcome, especially for:

- New transcript source adapters;
- Better transcript cleanup and speaker detection;
- Corrections to confidence-audit rules based on real cases;
- Improvements to Lark document structure and visual quality.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting a change.

---

<div align="center">
  <strong>Transcript → Evidence → Insight</strong><br/>
  <sub>Turn long-form media into conclusions people can verify and reuse.</sub>
</div>
