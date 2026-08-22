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

Before inspecting media, make the material choice and complete the reference gate in this order:

1. **Material type:** ask first for `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`; default `mixed`. Also record whether the stated scope contains `photo`, `video`, or both. Read only the chosen profile in [references/category-profiles.md](references/category-profiles.md). Mixed mode routes each item separately.
2. **Show and select automatic public sources:** use [references/reference-source-map.json](references/reference-source-map.json) to show the applicable no-login automatic sources for the material type and media kinds before research. The user may select a subset; if they make no selection, use the type-specific defaults. For `custom`, route from the brief. User-provided URLs or images remain user inputs, never routed catalog sources.
3. **Offer optional manual enhancement:** after the automatic selection, show the applicable subset of YouTube, Bilibili, Vimeo, Instagram, and Xiaohongshu. Never offer X. Declining or being unable to use manual enhancement must continue with the selected automatic public sources without blocking.
4. **Keep authentication user-managed:** if manual enhancement is selected, open the source in the user's default external browser unless the user explicitly chooses another browser or the default browser is unavailable. Instruct the user to complete any login or challenge themselves there, then confirm readiness and the selected sources. Use the Codex in-app browser for authenticated manual enhancement only when the user explicitly chooses it. Never ask for, receive, store, or handle usernames, passwords, MFA codes, cookies, account credentials, or other authentication secrets. Never bypass protection. Use only content actually visible in that browser. After login readiness is confirmed, background inspection in the same browser is allowed; the browser does not need to remain foregrounded.
5. **Run automatic visual calibration:** visit the selected automatic sources without login, preferably in the Codex in-app browser so background work remains isolated and controllable. A source counts only when actual image content or video playback is visible in this run. Page-only access, text-only results, search snippets, thumbnails, metadata, or remembered site style do not count. Skip failures and record the attempted URLs, exact limitation, failure reason, and absence of usable samples.
6. **Apply the two-source gate:** automatic calibration is `ready` only when at least two suitable automatic sources return visible samples. One successful source is `partial`; none is `unavailable`. Manual evidence may enhance a ready automatic calibration but never substitutes for the two automatic sources. Record automatic, manual-enhanced, partial, unavailable, or static-authorized state truthfully.
7. For `unavailable`, state exactly: **“当前无法查阅参考网站，因此不能获得实时参考/近期趋势。”** For `partial`, state that only one automatic source returned visible samples and the two-source gate was not met. Ask whether the user agrees to continue with static aesthetic knowledge while retaining the recorded limitation. Without explicit agreement, pause before inventory or culling. Never silently downgrade or describe static knowledge as current observation.

### Reference video sampling

- Reference videos default to silent background sampling. They do not need to play from start to finish or remain in the foreground.
- For each useful reference, inspect a small set of representative intervals such as the opening, middle, ending, and any clearly distinct visual beat. Increase continuous viewing only when pacing, transitions, narrative, or sound materially affects the calibration.
- Confirm that the video actually decoded and that playback time advanced. A poster frame, thumbnail, title, or metadata alone is not playback evidence.
- Keep audio muted when calibrating visual style. Sample audio only when sound, spoken context, or edit rhythm is relevant.
- Bring a browser to the foreground only for user-managed login, challenges, permission prompts, or an explicit user request to watch the process.

After the reference gate validates as ready, confirm the read-only source and a new, separate output directory, then ask the remaining opening choices:

1. **Organization mode:** `link` or `copy`; default `link`. Explain that links use the least space. Copy mode makes lightweight files for human re-screening: directly reviewable photos are safely copied, RAW uses or generates JPEG, and selected high-resolution video intervals become about-720p clips instead of copying whole high-bitrate videos. This substantially reduces the review directory but is not zero-storage; confirm this trade-off before writing.
2. **Video delivery, when relevant:** in link mode, default to `timecodes` and offer separate new clips; in copy mode, default to lightweight `clips`. If copy mode uses explicit `timecodes`, keep only source/timecode mappings and do not copy whole source videos.

Never move, overwrite, or delete originals, and never reuse a non-empty output directory.

Read [references/selection-rubric.md](references/selection-rubric.md). Before every cull, read and follow [references/style-reference-sources.md](references/style-reference-sources.md) and [references/reference-calibration-schema.md](references/reference-calibration-schema.md). Use `watch` for scene-aware video evidence. Use `video-use` only for later exact-frame or creative editing.

## Workflow

1. Account for every canonical source in `reference-source-map.json`. Research every selected automatic source; mark unselected sources with a concrete `skip_reason`. For a failed selected source, record it as failed and skipped from calibration rather than replacing visible evidence with page text or a remembered style.
2. If manual enhancement was selected and the user confirmed readiness, inspect only the selected sources in the user's visible browser. Record each source's visible samples and limitations. A failed or protected source is skipped honestly; do not request authentication data or bypass the protection.
3. Record `reference-calibration.json` using [references/reference-calibration-schema.md](references/reference-calibration-schema.md): selection basis, automatic status, manual status, access time, search path, actual visible samples, per-source limitations/failures, observed patterns, and the applied selection rules.
4. Synthesize automatic cross-source patterns only from visible samples repeated across at least two suitable automatic sources. Keep long-term standards, optional manual trend/author signals, and single-author signatures separate. Likes, views, ratings, and ranking are discovery signals only.
5. Run `python3 scripts/validate_reference_calibration.py --input <reference-calibration.json>`. Continue on `ready-automatic`, `ready-manual-enhanced`, or an explicitly authorized static result. Exit `3` means the automatic result is partial/unavailable and screening must pause for the user's static-fallback decision; exit `2` means repair the evidence log before culling.
6. Inventory read-only: paths, type, dimensions or duration, capture time, corruption, and duplicate groups.
7. Inspect representative frames and useful long-video intervals.
8. Apply the validated reference calibration plus aesthetic/story and relationship/memory channels. Relationship value may rescue imperfect media when the interaction remains discernible.
9. Run the normal first-pass classification as `select`, `review`, `memory`, or `excluded`. Do not ask about a backup percentage in the opening prompt.
10. Deduplicate the candidate denominator: RAW+JPEG pairs and byte-identical files count once. Calculate `review_unique_candidates / unique_candidates`. The default review ceiling is 20%, or an explicit user-supplied alternative. It is a conditional ceiling, never a quota: at or below it, change nothing and never add weak items to fill it.
11. Only above the ceiling, run backup overflow reduction until the deduplicated review ratio is at or below the ceiling. Remove redundancy first. An ordinary unchanged burst normally keeps at most 1–2 genuinely distinct `review` alternatives; an irreplaceable relationship progression may keep 3–5 only for distinct setup, peak, resolution, or relationship beats. Move usable remainder to `not_selected`, not `excluded` or `memory`.
12. Choose retained representatives with the active category profile and validated reference calibration. For posed portraits or groups, prefer visible unobstructed faces, open eyes, natural or engaging expressions, suitable camera-facing gaze, composition, light, focus, and timing. For candid, documentary, or family interaction, let emotion, relationship, interaction, and story beat outweigh direct gaze when stronger. Popularity metrics never replace judgment.
13. Create a UTF-8 CSV manifest with `source_path,decision,reason,start_time,end_time`. Use one row per useful video interval. For deterministic overflow handling, add `candidate_id,similarity_group,relationship_progression,story_beat,representative_score,capture_style,selection_evidence`; blank values remain valid. Optionally add `paired_jpeg_path` for a known RAW+JPEG pair; otherwise same-stem `.jpg`/`.jpeg` is detected automatically.
14. Run `scripts/build_review_set.py --manifest <csv> --output <dir> --mode link|copy --video-delivery auto|timecodes|clips [--review-ceiling 0.20]`. Prefer `auto`: copy mode exports lightweight clips, link mode keeps timecodes. The script prints a rough, non-zero storage estimate before generation and records both the first-pass and final review ratios.
15. Inspect `generation_status`, `review_asset_kind`, and `generation_detail` in `筛选清单.csv`; inspect `未入选清单.csv` separately from `排除清单.csv`. Verify counts, mappings, playable clips, links, sources, and reasons. Exit status `3` means the review set exists but one or more derivatives failed; do not present it as fully successful.
16. Report uncertainty instead of rejecting guesses. Map every review file back to its high-quality original and tell the user to use originals for final editing.

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
