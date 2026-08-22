# Shining Moments

English | [简体中文](README.md)

<p align="center">
  <a href="https://github.com/ErdonChen/Shining-Moments-Cut/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ErdonChen/Shining-Moments-Cut?style=flat-square"></a>
  <a href="https://github.com/ErdonChen/Shining-Moments-Cut/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ErdonChen/Shining-Moments-Cut/ci.yml?branch=main&amp;style=flat-square&amp;label=CI"></a>
  <a href="../../LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square"></a>
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-111111?style=flat-square">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white">
</p>

## Name inspiration

**Shining Moments** is inspired by the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” means both aesthetically strong frames and technically imperfect but irreplaceable moments of family, friendship, and life.

## Core highlights

Shining Moments is an intelligent “first filter”: it narrows the review set while leaving the final choice to the user.

- **Choose the material type before applying criteria:** Start with Mixed, Landscape/Travel, Architecture/Space, Documentary/Culture, Portrait, Family, Friends, Vlog/Event, or Custom. Each type uses targeted criteria instead of repeatedly applying one generic scoring template.
- **Run a fixed no-login automatic calibration:** Photos use Wikimedia Commons Images, public Flickr content, and Google Images; videos use Wikimedia Commons Videos and Google Videos. Users no longer check individual automatic sites. Photo and video gates are separate, and each requested kind needs at least two distinct sources with media actually visible or playable in this run.
- **Use at most one manual enhancement per run:** After automatic calibration, the user may choose human-verification enhancement (Unsplash photos or Pexels photos/videos), user-login enhancement (Xiaohongshu, Instagram, YouTube, or Bilibili), or another URL. The Skill recommends only one best-fit source. One Pexels challenge can be reused for both photos and videos.
- **Keep quality ahead of soft ratio guardrails:** The 10% primary and 25% review ratios only trigger a second pass that detects indiscriminate selection; they are not hard caps or quotas. Meaningful, high-quality, usable, non-redundant media may exceed them with recorded evidence. Video ratios use total source duration and interval unions, not file counts.
- **Organize photos and videos consistently, with a separate emotional channel:** The review set is divided into selects, alternatives for re-screening, and memory keeps. Family, friendship, and irreplaceable emotional moments can be preserved independently of purely technical quality.
- **Copy mode automatically stays lightweight instead of hauling large sources:** Link mode uses the least space. Copy mode is designed for human re-screening: it prefers a paired JPEG for RAW or generates a JPEG review copy, and exports only selected 4K/1080p intervals as about-720p review clips instead of copying whole high-bitrate videos. This can substantially reduce review-directory storage, but it is not zero-storage; the script estimates space first.
- **Keep every derivative traceable and every original safe:** Photo, video, and lightweight-copy records preserve the original path, category, reason, and timecode mapping. Originals are never moved, overwritten, or deleted, and final editing should use the originals.

An intelligent first-pass curation Skill for personal photos and videos. It removes only confidently unusable media, then leaves selects, usable alternatives, duplicates, and relationship-rich moments for the user's final review.

## Agent and model compatibility

Shining Moments is not Codex-only. Its core `SKILL.md`, category and selection rules, `references/` materials, and `scripts/build_review_set.py` organizer are model-independent. Any agent that can read these files and access the required tools can follow the same workflow.

- **Codex on this machine:** It is currently installed at `~/.codex/skills/shining-moments`, the personal Codex Skills directory, so Codex can discover it automatically. Other agents must install the complete Skill directory in a Skills location they officially support, or be instructed to read `SKILL.md` directly.
- **GitHub Copilot:** GitHub documents `.github/skills/<skill-name>`, `.agents/skills/<skill-name>`, and `.claude/skills/<skill-name>` for project skills. Personal skills go in `~/.copilot/skills/<skill-name>` or `~/.agents/skills/<skill-name>`, with `SKILL.md` inside each skill directory. See [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) and [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).
- **Google's related agent environment:** The Antigravity runtime used by Gemini API managed agents can auto-discover a skill at `.agents/skills/<skill-name>/SKILL.md`. This does not imply that every Google chat product has the same capability. See [Building managed agents](https://ai.google.dev/gemini-api/docs/custom-agents).
- **Codex metadata:** `agents/openai.yaml` supplies Codex UI and invocation metadata. Other agents can ignore it without affecting the core Skill.

An ordinary chat model can still apply the written selection criteria and help reason about choices. Without local-file access, image/video analysis, and command-execution tools, however, it cannot automatically inventory media, create links or copies, or export video clips. For agents not listed above, do not assume automatic discovery; follow that product's official documentation or have it read `SKILL.md` directly.

Runtime requirements: Python 3.10+; generating a RAW review JPEG requires ImageMagick (`magick`), RawTherapee CLI, darktable CLI, or macOS `sips` with support for that camera format (no converter is needed when a paired JPEG exists); exporting video review clips requires `ffmpeg` and `ffprobe`; link mode requires operating-system support for symbolic links. If a converter or video tool is missing or fails, the script preserves the original mapping, records `not-generated` / `failed`, and returns a partial-success status instead of pretending an asset was generated.

## Four-step quick flow

First confirm that the originals are read-only. The Skill then gathers four simple choices:

| Step | User choice | What the Skill does |
|---|---|---|
| **1. Topic** | Mixed, Landscape/Travel, Architecture/Space, Documentary/Culture, Portrait, Family, Friends, Vlog/Event, or Custom | Applies the matching aesthetic, narrative, and relationship criteria; defaults to Mixed. |
| **2. Media kind** | Photos, Videos, or Photos + Videos | Calibrates and screens photos and videos separately. |
| **3. Reference calibration** | Use automatic sources, with one optional manual enhancement | Automatic photo sources are Commons, Flickr, and Google Images; automatic video sources are Commons and Google Videos. If needed, add one human-verification, user-login, or custom-URL source. |
| **4. Delivery** | Symbolic links (default) or lightweight copies | Links use the least space. Lightweight copies generate/reuse JPEGs for RAW and export only selected video intervals. Neither mode moves, overwrites, or deletes originals. |

Manual enhancement uses at most one source per run: Unsplash or Pexels (including Pexels Videos) for human verification; Xiaohongshu, Instagram, YouTube, or Bilibili for user login; or another reference URL supplied by the user. Verification and login happen only in the user's own visible browser. One Pexels challenge can be reused for both photos and videos. If the user declines or the enhancement fails, automatic calibration still continues. Each requested media kind needs at least two distinct sources actually visible or playable in this run; automatic and manual evidence may be combined.

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
- **10%/25% are soft triggers only:** if Primary exceeds 10% or Review exceeds 25%, run an automatic second pass that removes redundancy, weaker alternatives, generic filler, and video dead air first. These are neither quotas nor hard caps.
- **Quality exceptions:** meaningful, high-quality, usable, non-redundant media may exceed the triggers when concrete evidence is recorded. There is no second percentage cap. Ordinary Primary overflow moves to Review; ordinary Review overflow moves to Not Selected, never Memory or Excluded.
- **Separate denominators:** photos use the deduplicated candidate count, with RAW+JPEG and exact duplicates counted once. Videos use deduplicated readable source duration and interval unions, not video file count. A readable video collection totaling 60 seconds or less keeps its natural first pass.

## Output structure

```text
01_主选/
02_备选_用户复筛/
03_纪念留档/
筛选清单.csv
未入选清单.csv
排除清单.csv
筛选报告.md
```

## Reference sites

Use these sources to calibrate composition, light, gesture, pacing, and narrative. Do not copy individual works or treat likes and views as quality scores. The order is a fixed no-login automatic pass followed by at most one human-verification, user-login, or custom-URL enhancement. This is the single authoritative user-facing source table.

| Flow layer | Photo sources | Video sources | User action and rule |
|---|---|---|---|
| **1. No-login automatic calibration (always runs)** | [Wikimedia Commons Images](https://commons.wikimedia.org/wiki/Category:Images): place, architecture, history, culture, and documentary context.<br>[Public Flickr content](https://www.flickr.com/explore): real events, street, community, and personal perspectives.<br>[Google Images](https://images.google.com/): broad cross-site discovery; enlarged previews require a recorded origin URL, and thumbnails do not count. | [Wikimedia Commons Videos](https://commons.wikimedia.org/wiki/Category:Videos): documentary, historical, cultural, location, and public-media motion references.<br>[Google Videos](https://www.google.com/videohp): cross-site discovery of action, pacing, shot structure, and topic-specific video. | Do not ask the user to check individual sites. Only full images/qualified enlarged previews or actual video playback count. Google Images and Google Videos each count as one source. |
| **2A. Optional human-verification enhancement (at most one)** | [Unsplash](https://unsplash.com/): curated composition, light, travel, portrait, and lifestyle photos.<br>[Pexels](https://www.pexels.com/): people, lifestyle, and general-scene photos. | [Pexels Videos](https://www.pexels.com/videos/): action, shot structure, and general B-roll. | Recommend one source by topic/media kind. The user completes the challenge in their own visible browser. One Pexels challenge can be reused for both photos and videos; do not ask for a second challenge. |
| **2B. Optional user-login enhancement (at most one)** | [Xiaohongshu](https://www.xiaohongshu.com/explore): Chinese-language lifestyle, travel, and local context.<br>[Instagram](https://www.instagram.com/): contemporary portrait, lifestyle, and creator photo language. | [YouTube](https://www.youtube.com/): long- and short-form narrative, shot organization, and editing structure.<br>[Bilibili](https://www.bilibili.com/): Chinese-language Vlogs, events, culture, and community video.<br>Xiaohongshu and Instagram: short-video and contemporary visual expression. | Recommend one source by topic/language. The user chooses the site and logs in themselves in their own visible browser. |
| **2C. User-supplied custom URL** | Any photo-reference site entered by the user | Any video-reference site entered by the user | Open the URL first. Use public visible media directly, ask the user to complete a challenge if one appears, and ask them to log in only if the site actually requires it. |

During manual enhancement, the Skill **never asks for, receives, stores, or handles** usernames, passwords, MFA codes, cookies, API keys, account credentials, or other authentication secrets, and it never bypasses protection. If the user declines or cannot use manual enhancement, automatic calibration still continues and is not cancelled.

X and Vimeo are not routed sources. A loaded page, text, search snippet, thumbnail, or remembered platform style does not count as visual calibration. Photos and videos each need two sources visible in this run; one is partial and zero is unavailable. Screening pauses unless the user explicitly authorizes static standards.

## Usage

Invoke it in Codex with:

```text
Use $shining-moments to curate this photo and video folder.
```
