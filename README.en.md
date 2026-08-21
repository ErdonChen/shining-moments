# Shining Moments

English | [简体中文](README.md)

A conservative first-pass curation Skill for personal photos and videos. It removes only confidently unusable media, then leaves selects, usable alternatives, duplicates, and relationship-rich moments for the user's final review.

## Name inspiration

**Shining Moments** is inspired by the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” means both aesthetically strong frames and technically imperfect but irreplaceable moments of family, friendship, and life.

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
