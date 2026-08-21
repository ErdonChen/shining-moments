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
- **Calibrate aesthetics with category-relevant references, not popularity:** Landscape and architecture can draw from 500px, YouTube, and ShotDeck; portrait and documentary work can draw from LensCulture and Magnum Photos; relationship footage and video storytelling can also draw from Vimeo Staff Picks. Instagram, Xiaohongshu, and X are trend signals only—likes never replace visual-language or narrative judgment. See the [full categorized reference list](#reference-sites).
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

## The three opening choices

First confirm the source and a new output directory, then ask these three questions in order.

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

### Step 2: Choose the organization mode

- **Symbolic links (default):** do not duplicate media content and use the least space; links, manifests, and reports still occupy a small amount.
- **Copies:** create lightweight files for human re-screening. Directly reviewable JPEG/HEIC/PNG and similar photos keep the safe copy behavior; RAW becomes a JPEG review copy, and selected 4K/1080p intervals become about-720p review clips. Copy mode does not directly copy large RAW files or whole high-bitrate videos, but it still uses storage and shows an estimate before execution.

When Copies is selected, the Skill restates and confirms this lightweight-derivative and storage trade-off before writing. Neither mode moves, overwrites, or deletes originals. A non-empty output directory is rejected to protect previous results.

### Step 3: Choose video delivery

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

Use these sources to calibrate composition, light, gesture, pacing, and narrative. Do not copy individual works or treat likes and views as quality scores.

| Category | References |
|---|---|
| Landscape, travel, and place | [500px](https://500px.com/), [YouTube](https://www.youtube.com/), [ShotDeck](https://shotdeck.com/), [National Geographic Photography](https://www.nationalgeographic.com/photography/) |
| Architecture and space | [ArchDaily](https://www.archdaily.com/), [Dezeen](https://www.dezeen.com/), ShotDeck |
| Portrait, people, and documentary | [LensCulture](https://www.lensculture.com/), [Magnum Photos](https://www.magnumphotos.com/), Instagram, Xiaohongshu |
| Family, relatives, and friendship | [Documentary Family Awards](https://documentaryfamilyawards.com/), [Family Photojournalist Association](https://www.fpja.com/), [This Is Reportage](https://thisisreportage.com/), Xiaohongshu |
| Video rhythm and emotional storytelling | [Vimeo Staff Picks](https://vimeo.com/channels/staffpicks), [NOWNESS](https://www.nowness.com/), YouTube |
| Trend and creator discovery | Instagram, Xiaohongshu, and [X](https://x.com/); discovery only, never popularity-based scoring |

## Usage

Invoke it in Codex with:

```text
Use $shining-moments to curate this photo and video folder.
```
