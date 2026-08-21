# Shining Moments

English | [简体中文](README.md)

<p align="center">
  <a href="https://github.com/ErdonChen/shining-moments/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ErdonChen/shining-moments?style=flat-square"></a>
  <a href="https://github.com/ErdonChen/shining-moments/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ErdonChen/shining-moments/ci.yml?branch=main&amp;style=flat-square&amp;label=CI"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square"></a>
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-111111?style=flat-square">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white">
</p>

## Core highlights

Shining Moments is a conservative “first filter”: it narrows the review set while leaving the final choice to the user.

- **Choose the material type before applying criteria:** Start with Mixed, Landscape/Travel, Architecture/Space, Documentary/Culture, Portrait, Family, Friends, Vlog/Event, or Custom. Each type uses targeted criteria instead of repeatedly applying one generic scoring template.
- **Start with automatic public references, then optionally enhance:** After the material type is known, show the applicable no-login photo/video sources. The user may select sources; no selection uses the type-specific defaults. Automatic calibration requires actual visible media from at least two suitable sources in the current run. YouTube, Bilibili, Vimeo, Instagram, and Xiaohongshu are optional manual enhancement only. See the [layered reference rules](#reference-sites).
- **Organize photos and videos consistently, with a separate emotional channel:** The review set is divided into selects, alternatives for re-screening, and memory keeps. Family, friendship, and irreplaceable emotional moments can be preserved independently of purely technical quality.
- **Copy mode automatically stays lightweight instead of hauling large sources:** Link mode uses the least space. Copy mode is designed for human re-screening: it prefers a paired JPEG for RAW or generates a JPEG review copy, and exports only selected 4K/1080p intervals as about-720p review clips instead of copying whole high-bitrate videos. This can substantially reduce review-directory storage, but it is not zero-storage; the script estimates space first.
- **Keep every derivative traceable and every original safe:** Photo, video, and lightweight-copy records preserve the original path, category, reason, and timecode mapping. Originals are never moved, overwritten, or deleted, and final editing should use the originals.

A conservative first-pass curation Skill for personal photos and videos. It removes only confidently unusable media, then leaves selects, usable alternatives, duplicates, and relationship-rich moments for the user's final review.

## Name inspiration

**Shining Moments** is inspired by the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” means both aesthetically strong frames and technically imperfect but irreplaceable moments of family, friendship, and life.

## Agent and model compatibility

Shining Moments is not Codex-only. Its core `SKILL.md`, category and selection rules, `references/` materials, and `scripts/build_review_set.py` organizer are model-independent. Any agent that can read these files and access the required tools can follow the same workflow.

- **Codex on this machine:** It is currently installed at `~/.codex/skills/shining-moments`, the personal Codex Skills directory, so Codex can discover it automatically. Other agents must install the complete Skill directory in a Skills location they officially support, or be instructed to read `SKILL.md` directly.
- **GitHub Copilot:** GitHub documents `.github/skills/<skill-name>`, `.agents/skills/<skill-name>`, and `.claude/skills/<skill-name>` for project skills. Personal skills go in `~/.copilot/skills/<skill-name>` or `~/.agents/skills/<skill-name>`, with `SKILL.md` inside each skill directory. See [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) and [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).
- **Google's related agent environment:** The Antigravity runtime used by Gemini API managed agents can auto-discover a skill at `.agents/skills/<skill-name>/SKILL.md`. This does not imply that every Google chat product has the same capability. See [Building managed agents](https://ai.google.dev/gemini-api/docs/custom-agents).
- **Codex metadata:** `agents/openai.yaml` supplies Codex UI and invocation metadata. Other agents can ignore it without affecting the core Skill.

An ordinary chat model can still apply the written selection criteria and help reason about choices. Without local-file access, image/video analysis, and command-execution tools, however, it cannot automatically inventory media, create links or copies, or export video clips. For agents not listed above, do not assume automatic discovery; follow that product's official documentation or have it read `SKILL.md` directly.

Runtime requirements: Python 3.10+; generating a RAW review JPEG requires ImageMagick (`magick`), RawTherapee CLI, darktable CLI, or macOS `sips` with support for that camera format (no converter is needed when a paired JPEG exists); exporting video review clips requires `ffmpeg` and `ffprobe`; link mode requires operating-system support for symbolic links. If a converter or video tool is missing or fails, the script preserves the original mapping, records `not-generated` / `failed`, and returns a partial-success status instead of pretending an asset was generated.

## The four opening steps

First confirm the source and a new output directory, then complete these four steps in order.

### Step 1: Choose the material type

| Option | Main emphasis |
|---|---|
| Mixed | Route each photo or video interval to its most relevant category |
| Landscape and travel | Light, weather, depth, sense of place, and travel progression |
| Architecture and space | Geometry, scale, material, circulation, and human use of space |
| Documentary and culture | Authentic action, environmental context, cultural detail, and dignity |
| Portrait | Expression, gaze, gesture, identity, skin tone, and background control |
| Family | Relationship clarity, emotional truth, family rhythm, and irreplaceability |
| Friends | Shared action, mutual reaction, chemistry, support, and group relationships |
| Vlog and events | Narrative role, progression, shot variety, sound, and editability |
| Custom | Build criteria from the deliverable, audience, must-keeps, and references |

The default is Mixed. Relationship and memory value remain safety channels even when another category is selected.

### Step 2: Choose reference sources

The Skill first shows the automatic public sources applicable to the material type and photo/video scope. The user may select a subset; no selection uses the type-specific defaults. Automatic sources require no login, and only full images or playable videos actually visible in the current run count as calibration evidence.

After automatic selection, the Skill offers optional manual-enhancement sources. Declining or being unable to use manual enhancement never blocks the task; the workflow continues with automatic public sources. See [Reference sites](#reference-sites) for the layered source list and authentication boundary.

### Step 3: Choose the organization mode

- **Symbolic links (default):** do not duplicate media content and use the least space; links, manifests, and reports still occupy a small amount.
- **Copies:** create lightweight files for human re-screening. Directly reviewable JPEG/HEIC/PNG and similar photos keep the safe copy behavior; RAW becomes a JPEG review copy, and selected 4K/1080p intervals become about-720p review clips. Copy mode does not directly copy large RAW files or whole high-bitrate videos, but it still uses storage and shows an estimate before execution.

When Copies is selected, the Skill restates and confirms this lightweight-derivative and storage trade-off before writing. Neither mode moves, overwrites, or deletes originals. A non-empty output directory is rejected to protect previous results.

### Step 4: Choose video delivery

- **Link mode defaults to timecodes only:** link the whole source and record recommended intervals; separate new clips remain an explicit option.
- **Copy mode defaults to lightweight candidate clips:** timed included intervals in Select, Review, and Memory become new H.264/AAC MP4 files. Landscape output is capped at 1280×720 and portrait output at 720×1280; sources already at or below those bounds are never enlarged or stretched.
- **Copy mode with explicit timecodes only:** preserve original-path and timecode mappings without copying the whole video.

Clip export requires `ffmpeg` and `ffprobe`. Timecodes are validated against source duration. HDR/HLG, rotation metadata, or variable frame rate triggers a short sample check for color tagging, orientation, playability, and audio/video duration drift before the full candidate interval is exported. A failure never falls back to copying the whole source video.

## Lightweight-copy manifest and example

The input CSV requires at least `source_path,decision,reason`. Add `start_time,end_time` for video intervals and optional `paired_jpeg_path` for a known RAW+JPEG pair. When that field is empty, the script first looks for a same-directory, same-stem `.jpg`/`.jpeg`.

```bash
python3 scripts/build_review_set.py \
  --manifest shortlist.csv \
  --output review-set \
  --mode copy \
  --video-delivery auto
```

Example mappings from `shortlist.csv` to review derivatives:

| High-quality original | Review derivative | Manifest record |
|---|---|---|
| `/media/IMG_1234.CR3` | `01_主选/IMG_1234__review.jpg` | `paired-jpeg` or `generated-jpeg`; records both the RAW original path and review JPEG path |
| `/media/GH010042.MP4` at `00:01:12–00:01:24` | `01_主选/GH010042__00-01-12_to_00-01-24.mp4` | `video-review-clip`; records original path, timecodes, category, and reason, with 4K/1080p sources delivered at about 720p |

`筛选清单.csv` also records `review_source_path`, `organized_path`, `review_asset_kind`, `generation_status`, and `generation_detail`. Asset kinds distinguish source links/ordinary copies, existing paired JPEGs, newly generated JPEGs, 720p candidate clips, timecode-only mappings, and ungenerated failures. Filename collisions receive stable `__2`, `__3`, ... suffixes instead of overwriting an output.

## First-pass rules

- **Two judgment channels:** aesthetic/story value and relationship/memory value.
- **`select`:** strongest first-pass recommendations, still subject to user approval.
- **`review`:** usable, uncertain, repairable, duplicate, or relationship-protected media.
- **`memory`:** emotionally significant media not recommended for a normal edit.
- **`excluded`:** confidently unusable, non-sentimental media; record the reason without creating a link or copy.
- **Duplicates:** recommend one representative when appropriate and keep every other usable version in Review.
- **Shaky video:** ordinary footage may be excluded when reasonable stabilization cannot recover it; recognizable family or friendship interaction stays in Review; visually unrecognizable but known sentimental material goes to Memory only.
- **Long video:** judge intervals independently and record precise timecodes; never condemn a whole source from one bad frame.

## Output structure

```text
01_主选/
02_备选_用户复筛/
03_纪念留档/
筛选清单.csv
排除清单.csv
筛选报告.md
```

## Reference sites

Use these sources to calibrate composition, light, gesture, pacing, and narrative. Do not copy individual works or treat likes and views as quality scores. The Skill dynamically routes an applicable subset by material type; this table is the single authoritative user-facing source explanation.

| Source layer | Photo sites | Video sites | Rule |
|---|---|---|---|
| Automatic public sources | [Unsplash](https://unsplash.com/), [Pexels Photos](https://www.pexels.com/), [public Flickr content](https://www.flickr.com/explore), [Wikimedia Commons images](https://commons.wikimedia.org/wiki/Main_Page) | [Pexels Videos](https://www.pexels.com/videos/), [Pixabay Videos](https://pixabay.com/videos/), [Mixkit](https://mixkit.co/free-stock-video/), and [Wikimedia Commons videos](https://commons.wikimedia.org/wiki/Category:Videos) when suitable | No login. The user may select sources; no selection uses the type default. Only full images or video playback actually visible in this run count, and automatic visual calibration requires at least two suitable sources. |
| Optional manual enhancement | [Instagram](https://www.instagram.com/) and [Xiaohongshu](https://www.xiaohongshu.com/explore) | [YouTube](https://www.youtube.com/), [Bilibili](https://www.bilibili.com/), [Vimeo](https://vimeo.com/), Instagram, and Xiaohongshu | The user must complete login or challenges themselves in their own visible browser, then confirm readiness and selected sources. Use only content actually visible there. |

During manual enhancement, the Skill **never asks for, receives, stores, or handles** usernames, passwords, MFA codes, cookies, account credentials, or other authentication secrets, and it never bypasses protection. If the user declines or cannot use manual enhancement, the workflow falls back to and continues with automatic public sources without blocking.

X is not an automatic route and is never offered for manual enhancement. User-provided URLs or images remain user inputs rather than routed sources or automatic-connectivity evidence. A loaded page, text, search snippet, thumbnail, or remembered platform style does not count as visual calibration.

## Usage

Invoke it in Codex with:

```text
Use $shining-moments to curate this photo and video folder.
```
