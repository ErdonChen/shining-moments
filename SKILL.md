---
name: shining-moments
description: Use when conservatively screening, culling, shortlisting, or organizing personal photos and videos before the user makes the final selection, including travel, Vlog, family, friends, and relationship-centered footage.
---

# Shining Moments

## Name and intent

The name *Shining Moments* echoes the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” includes both aesthetically outstanding frames and technically imperfect but irreplaceable moments of family, friendship, and life.

## Core principle

Remove only confidently unusable material. Preserve usable, uncertain, duplicate, and relationship-rich media for the user’s final judgment.

## Start every task

Ask one compact opening prompt in this order:

1. **Material type first:** `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`; default `mixed`. Read only its profile in [references/category-profiles.md](references/category-profiles.md). Mixed mode routes each item separately.
2. **Paths:** source and a new, separate output directory.
3. **Storage:** symbolic links or copies; default links. Recommend copies only for small portable sets.
4. **Video delivery, when relevant:** `timecodes` or `clips`; default `timecodes`. Clips consume storage and export timed `select` and `review` intervals.

Never move or delete originals, and never reuse a non-empty output directory.

Read [references/selection-rubric.md](references/selection-rubric.md). Read [references/style-reference-sources.md](references/style-reference-sources.md) only when current examples are needed. Use `watch` for scene-aware video evidence. Use `video-use` only for later exact-frame or creative editing.

## Workflow

1. Inventory read-only: paths, type, dimensions or duration, capture time, corruption, and duplicate groups.
2. Inspect representative frames and useful long-video intervals.
3. Apply aesthetic/story and relationship/memory channels. Relationship value may rescue imperfect media when the interaction remains discernible.
4. Classify as `select`, `review`, `memory`, or `excluded`. A duplicate group may have one `select`; every other usable member goes to `review`.
5. Create a UTF-8 CSV manifest with at least `source_path,decision,reason,start_time,end_time`. For a partially useful video, keep one row per recommended interval.
6. Run `scripts/build_review_set.py --manifest <csv> --output <dir> --mode link|copy --video-delivery timecodes|clips`. Clips require valid in-duration timecodes and `ffmpeg`; they are new source-stream-copy files and may align to nearby keyframes.
7. Verify counts, links, sources, and exclusion reasons. Report uncertainty instead of rejecting guesses.

## Non-negotiable boundaries

- This is first-pass curation, not the final edit.
- `timecodes`: keep the whole source once, ordered by `select` > `review` > `memory`; export no segments or previews.
- `clips`: export only timed `select` and `review` intervals; never normal-edit exports for `memory` or `excluded`.
- Unrecoverably shaky ordinary footage may be excluded. Recognizable relationship footage stays `review`; unrecognizable known sentimental footage is `memory`.
- `excluded` receives no link or copy; record its original path and concrete reason.
- Never move, delete, or recommend deleting originals.

## Output contract

- `01_主选/`
- `02_备选_用户复筛/`
- `03_纪念留档/`
- `筛选清单.csv`
- `排除清单.csv`
- `筛选报告.md`
