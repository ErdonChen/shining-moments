---
name: shining-moments
description: Use when conservatively screening, culling, shortlisting, or organizing personal photos and videos before the user makes the final selection, including travel, Vlog, family, friends, and relationship-centered footage.
---

# Shining Moments

## Name and intent

The name *Shining Moments* echoes the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” includes both aesthetically outstanding frames and technically imperfect but irreplaceable moments of family, friendship, and life.

## Core principle

This is a conservative first filter, not a final edit. Remove only confidently unusable material. Preserve usable, uncertain, duplicate, and relationship-rich media for the user’s final judgment.

## Start every task

Confirm the read-only source and a new, separate output directory, then ask one compact opening prompt in this order:

1. **Material type:** `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`; default `mixed`. Read only its profile in [references/category-profiles.md](references/category-profiles.md). Mixed mode routes each item separately.
2. **Organization mode:** `link` or `copy`; default `link`. Explain that links use the least space. Copy mode makes lightweight files for human re-screening: directly reviewable photos are safely copied, RAW uses or generates JPEG, and selected high-resolution video intervals become about-720p clips instead of copying whole high-bitrate videos. This substantially reduces the review directory but is not zero-storage; confirm this trade-off before writing.
3. **Video delivery, when relevant:** in link mode, default to `timecodes` and offer separate new clips; in copy mode, default to lightweight `clips`. If copy mode uses explicit `timecodes`, keep only source/timecode mappings and do not copy whole source videos.

Never move, overwrite, or delete originals, and never reuse a non-empty output directory.

Read [references/selection-rubric.md](references/selection-rubric.md). Read [references/style-reference-sources.md](references/style-reference-sources.md) only when current examples are needed. Use `watch` for scene-aware video evidence. Use `video-use` only for later exact-frame or creative editing.

## Workflow

1. Inventory read-only: paths, type, dimensions or duration, capture time, corruption, and duplicate groups.
2. Inspect representative frames and useful long-video intervals.
3. Apply aesthetic/story and relationship/memory channels. Relationship value may rescue imperfect media when the interaction remains discernible.
4. Classify each item or interval as `select`, `review`, `memory`, or `excluded`. A duplicate group may have one `select`; every other usable member goes to `review`.
5. Create a UTF-8 CSV manifest with `source_path,decision,reason,start_time,end_time`. Use one row per useful video interval. Optionally add `paired_jpeg_path` for a known RAW+JPEG pair; otherwise same-stem `.jpg`/`.jpeg` is detected automatically.
6. Run `scripts/build_review_set.py --manifest <csv> --output <dir> --mode link|copy --video-delivery auto|timecodes|clips`. Prefer `auto`: copy mode exports lightweight clips, link mode keeps timecodes. The script prints a rough, non-zero storage estimate before generation.
7. Inspect `generation_status`, `review_asset_kind`, and `generation_detail` in `筛选清单.csv`. Verify counts, mappings, playable clips, links, sources, and exclusion reasons. Exit status `3` means the review set exists but one or more derivatives failed; do not present it as fully successful.
8. Report uncertainty instead of rejecting guesses. Map every review file back to its high-quality original and tell the user to use originals for final editing.

## Lightweight copy contract

- Directly reviewable non-RAW photos such as JPEG, HEIC, and PNG keep the existing safe copy behavior.
- For RAW, prefer the manifest-provided or same-stem paired JPEG. Record both the RAW original and reused JPEG review source. Without a pair, use an available converter to create a quality-85 JPEG review copy with usable orientation and color handling.
- Converter resolution checks `magick`, `rawtherapee-cli`, `darktable-cli`, then macOS `sips`; actual camera-format support varies. If unavailable or conversion fails, create no fake output: record `not-generated` / `failed`, retain the original mapping, provide a dependency hint, and return partial-success status `3`.
- For every timed included video (`select`, `review`, or `memory`), create a new MP4 review clip using H.264/AAC. Cap landscape at 1280×720 and portrait at 720×1280 while preserving aspect ratio; never upscale a source already at or below those bounds.
- For HDR/HLG, rotation metadata, or variable frame rate, render and validate a short sample before the full interval. Check color tagging, display orientation, playability, and audio/video duration drift. A failed export remains explicitly mapped as `not-generated` / `failed`.
- Never copy a whole source video in copy mode. `timecodes` records source intervals only; `clips` exports only the listed included intervals. Duplicate interval rows reuse the same derivative; distinct collisions receive stable `__2`, `__3`, ... names without overwriting.

## Non-negotiable boundaries

- Keep final choice with the user.
- `link + timecodes`: link each included source once, ordered by `select` > `review` > `memory`, and retain every interval in the manifest.
- `copy + timecodes`: do not copy whole videos; retain their original paths and timecodes in the report and manifest.
- `clips`: create lightweight review derivatives for timed included intervals only. A `memory` clip remains a sentimental review item, not a normal-edit recommendation.
- Unrecoverably shaky ordinary footage may be excluded. Recognizable relationship footage stays `review`; unrecognizable known sentimental footage is `memory`.
- `excluded` receives no link, copy, or clip; record its original path and concrete reason.
- Never move, overwrite, delete, or recommend deleting originals.

## Output contract

- `01_主选/`
- `02_备选_用户复筛/`
- `03_纪念留档/`
- `筛选清单.csv`
- `排除清单.csv`
- `筛选报告.md`
