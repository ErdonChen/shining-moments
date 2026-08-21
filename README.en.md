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
- **Choose the delivery method without touching originals:** Use symbolic links or copies; for video, keep timecodes only or export new candidate clips. Original files are never moved, overwritten, or deleted.

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

Runtime requirements: Python 3.10+; exporting new video candidate clips requires `ffmpeg` and `ffprobe`; link mode requires operating-system support for symbolic links.

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

- **Symbolic links (default):** use no additional media storage; best for large collections.
- **Copies:** create portable review files; best for smaller collections.

Neither mode moves, overwrites, or deletes originals. A non-empty output directory is rejected to protect previous results.

### Step 3: Choose video delivery

- **Timecodes only (default):** keep one whole-source link or copy and record the recommended start and end times.
- **Export separate new clips:** create new select or review clips for the user to screen directly. The original video is never trimmed or modified.

Clip export requires `ffmpeg` and `ffprobe`. Timecodes are validated against the source duration. Source audio and video streams are preserved to avoid generational loss, so rough cut boundaries may align to nearby keyframes.

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
