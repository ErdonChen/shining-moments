---
name: shining-moments
description: Use when conservatively screening, culling, shortlisting, or organizing personal photos and videos before the user makes the final selection, including travel, Vlog, family, friends, and relationship-centered footage.
---

# Shining Moments

## Name and intent

The name *Shining Moments* echoes the Japanese song title *煌めく瞬間に捕われて*, commonly rendered in Chinese as “捕捉闪耀的瞬间.” Here, “shining” includes both aesthetically outstanding frames and technically imperfect but irreplaceable moments of family, friendship, and life.

## Core principle

This is a conservative first filter, not a final edit. Remove only confidently unusable material as `excluded`. Preserve uncertainty and relationship value, while preventing a redundant backup set from becoming no filter at all. The user keeps the final choice.

## Start every task

Run **Connectivity check and live references** before inspecting media or asking for source/output paths:

1. Check whether the current environment can reach at least two public reference-site endpoints from [references/reference-source-map.json](references/reference-source-map.json). Use the environment's available connection as configured; do not require a particular connection method. Record time, endpoints, result, and limitation in `connectivity_check`.
2. If the check fails, state exactly: **“当前无法查阅参考网站，因此不能获得实时参考/近期趋势。”** Then ask whether the user agrees to continue with existing static aesthetic knowledge or prior impressions. Without explicit agreement, pause before inventory or culling. Never silently downgrade or describe static knowledge as live observation.
3. If connectivity succeeds, continue with live research. A successful opening check does not prove every source is accessible; record per-source restrictions honestly.

After that gate is ready, confirm the read-only source and a new, separate output directory, then ask one compact opening prompt in this order:

1. **Material type:** `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`; default `mixed`. Read only its profile in [references/category-profiles.md](references/category-profiles.md). Mixed mode routes each item separately.
2. **Organization mode:** `link` or `copy`; default `link`. Explain that links use the least space. Copy mode makes lightweight files for human re-screening: directly reviewable photos are safely copied, RAW uses or generates JPEG, and selected high-resolution video intervals become about-720p clips instead of copying whole high-bitrate videos. This substantially reduces the review directory but is not zero-storage; confirm this trade-off before writing.
3. **Video delivery, when relevant:** in link mode, default to `timecodes` and offer separate new clips; in copy mode, default to lightweight `clips`. If copy mode uses explicit `timecodes`, keep only source/timecode mappings and do not copy whole source videos.

Never move, overwrite, or delete originals, and never reuse a non-empty output directory.

Read [references/selection-rubric.md](references/selection-rubric.md). Before every cull, read and follow [references/style-reference-sources.md](references/style-reference-sources.md) and [references/reference-calibration-schema.md](references/reference-calibration-schema.md). Use `watch` for scene-aware video evidence. Use `video-use` only for later exact-frame or creative editing.

## Workflow

1. After connectivity succeeds and material type is known, account for every canonical source in `reference-source-map.json`. Visit every source required for the active type; each other source needs a concrete `skip_reason`. Search recent popular, featured, editor-selected, or representative public work rather than relying on remembered site style.
2. Record `reference-calibration.json`: access date, search terms, sample scope, visible curation or popularity mechanism, evidence URLs, access limitations, keywords, observed patterns, and whether evidence is editorial, recent trend, or one-author style. Restricted sites need a truthful limitation plus verifiable public fallback evidence; never pretend access succeeded.
3. Synthesize repeated cross-source patterns and translate them into project selection rules. Keep long-term editorial standards, recent platform trends, and individual-author signatures separate. Likes, views, ratings, and ranking are discovery signals only.
4. Run `python3 scripts/validate_reference_calibration.py --input <reference-calibration.json>`. Continue only on `ready-live` or `ready-static-authorized`. Exit `3` means pause for explicit user authorization; exit `2` means repair the evidence log before culling.
5. Inventory read-only: paths, type, dimensions or duration, capture time, corruption, and duplicate groups.
6. Inspect representative frames and useful long-video intervals.
7. Apply the validated reference calibration plus aesthetic/story and relationship/memory channels. Relationship value may rescue imperfect media when the interaction remains discernible.
8. Run the normal first-pass classification as `select`, `review`, `memory`, or `excluded`. Do not ask about a backup percentage in the opening prompt.
9. Deduplicate the candidate denominator: RAW+JPEG pairs and byte-identical files count once. Calculate `review_unique_candidates / unique_candidates`. The default review ceiling is 20%, or an explicit user-supplied alternative. It is a conditional ceiling, never a quota: at or below it, change nothing and never add weak items to fill it.
10. Only above the ceiling, run backup overflow reduction until the deduplicated review ratio is at or below the ceiling. Remove redundancy first. An ordinary unchanged burst normally keeps at most 1–2 genuinely distinct `review` alternatives; an irreplaceable relationship progression may keep 3–5 only for distinct setup, peak, resolution, or relationship beats. Move usable remainder to `not_selected`, not `excluded` or `memory`.
11. Choose retained representatives with the active category profile and validated reference calibration. For posed portraits or groups, prefer visible unobstructed faces, open eyes, natural or engaging expressions, suitable camera-facing gaze, composition, light, focus, and timing. For candid, documentary, or family interaction, let emotion, relationship, interaction, and story beat outweigh direct gaze when stronger. Popularity metrics never replace judgment.
12. Create a UTF-8 CSV manifest with `source_path,decision,reason,start_time,end_time`. Use one row per useful video interval. For deterministic overflow handling, add `candidate_id,similarity_group,relationship_progression,story_beat,representative_score,capture_style,selection_evidence`; blank values remain valid. Optionally add `paired_jpeg_path` for a known RAW+JPEG pair; otherwise same-stem `.jpg`/`.jpeg` is detected automatically.
13. Run `scripts/build_review_set.py --manifest <csv> --output <dir> --mode link|copy --video-delivery auto|timecodes|clips [--review-ceiling 0.20]`. Prefer `auto`: copy mode exports lightweight clips, link mode keeps timecodes. The script prints a rough, non-zero storage estimate before generation and records both the first-pass and final review ratios.
14. Inspect `generation_status`, `review_asset_kind`, and `generation_detail` in `筛选清单.csv`; inspect `未入选清单.csv` separately from `排除清单.csv`. Verify counts, mappings, playable clips, links, sources, and reasons. Exit status `3` means the review set exists but one or more derivatives failed; do not present it as fully successful.
15. Report uncertainty instead of rejecting guesses. Map every review file back to its high-quality original and tell the user to use originals for final editing.

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
- `not_selected` is usable but not shortlisted after judgment or overflow reduction. It receives no link, copy, or clip; retain its original path, first-pass decision, reason, and overflow action in `未入选清单.csv`.
- `memory` is independently justified sentimental material, never overflow storage used to evade the review ceiling. Distinct relationship beats may be protected; an entire near-identical burst is not protected by default.
- `excluded` is reserved for confidently unusable, corrupt, or unrecognizable non-sentimental media. It receives no link, copy, or clip; record its original path and concrete reason in `排除清单.csv`.
- Never move, overwrite, delete, or recommend deleting originals.

## Output contract

- `01_主选/`
- `02_备选_用户复筛/`
- `03_纪念留档/`
- `筛选清单.csv`
- `未入选清单.csv`
- `排除清单.csv`
- `筛选报告.md`
