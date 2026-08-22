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

Before inventory or media judgment, follow these four opening steps in order:

1. **1. Topic:** ask for `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`; default `mixed`. Read only the chosen profile in [references/category-profiles.md](references/category-profiles.md). Mixed mode routes each item separately.
2. **2. Media kinds:** ask for `photo`, `video`, or both. Keep photo and video reference gates, evidence, and selection ratios separate.
3. **3. Automatic calibration:** always run the fixed no-login pool for the requested media kinds: photo uses Wikimedia Commons Images, Flickr public content, and Google Images; video uses Wikimedia Commons Videos and Google Videos. Do not ask the user to choose individual automatic sites. A catalog source counts once, regardless of how many origin domains its search results expose.
   - **Optional manual enhancement:** after the automatic pass, ask whether the user wants one additional reference source. If yes, ask for `challenge`, `login`, or a custom URL, and recommend only one source for the active topic and media kinds. The user may accept, override, or type another URL.
   - **Keep browser access user-managed:** for a challenge, login, or custom URL that requires authentication, open the source in the user's default external browser unless the user explicitly chooses another browser or the default browser is unavailable. Use the Codex in-app browser for authenticated or challenged manual enhancement only when the user explicitly chooses it. After the user confirms readiness, background inspection in the same browser is allowed; the browser does not need to remain foregrounded.
   - For `challenge`, use Unsplash for photos or Pexels for photos and/or videos. The user completes the human-verification challenge in their own visible browser. One completed Pexels challenge can be reused for both Pexels Photos and Pexels Videos in the same run; do not ask for a second Pexels challenge.
   - For `login`, recommend one applicable source from Xiaohongshu, Instagram, YouTube, or Bilibili. The user chooses the site and logs in themselves in their own visible browser.
   - For a custom URL, open it first. Use public visible media directly; if a challenge appears, ask the user to complete it; ask the user to log in only when the site actually requires login.
   - Never ask for, receive, store, or handle usernames, passwords, MFA codes, cookies, API keys, account credentials, or other authentication secrets. Never bypass protection. Use only media actually visible in the user's browser. Declining or failing manual enhancement never cancels the automatic pass.
   - **Run automatic visual calibration:** inspect every fixed automatic source that applies to the requested media kind, preferably in the Codex in-app browser so no-login background work remains isolated and controllable. A photo counts only when a full image is visible; Google Images additionally permits an enlarged preview only when the origin URL is recorded. A video counts only when it actually plays. A page, text, metadata, search snippet, thumbnail, blocked player, or remembered style does not count. Google Images and Google Videos each count as one source, not as multiple origin sites.
   - Apply the two-source gate independently to photos and videos. Each requested media kind is ready only after at least two distinct catalog/custom sources provide visible evidence in this run. Automatic and successful manual evidence may combine; record the result as `automatic`, `manual-enhanced`, `partial`, `unavailable`, or `static-authorized`. If any requested kind has only one source, report `partial`; if none, report `unavailable`. Ask whether the user explicitly authorizes static aesthetic knowledge. Without that authorization, pause before inventory or culling and never present static knowledge as a current observation.
4. **4. Delivery mode:** after the reference gate is ready, confirm the read-only source and a new, separate output directory, then ask `link` or `copy`; default `link`. Link mode uses the least space and keeps video timecodes. Copy mode creates lightweight human-review derivatives: safe copies for directly reviewable photos, paired or generated JPEGs for RAW, and about-720p clips for included video intervals instead of whole high-bitrate videos. It is not zero-storage; confirm the trade-off before writing. Do not ask a separate video-delivery question unless the user requests an override.

### Reference video sampling

- Reference videos default to silent background sampling. They do not need to play from start to finish or remain in the foreground.
- For each useful reference, inspect a small set of representative intervals such as the opening, middle, ending, and any clearly distinct visual beat. Increase continuous viewing only when pacing, transitions, narrative, or sound materially affects the calibration.
- Confirm that the video actually decoded and that playback time advanced. A poster frame, thumbnail, title, or metadata alone is not playback evidence.
- Keep audio muted when calibrating visual style. Sample audio only when sound, spoken context, or edit rhythm is relevant.
- Bring a browser to the foreground only for user-managed login, challenges, permission prompts, or an explicit user request to watch the process.

Never move, overwrite, or delete originals, and never reuse a non-empty output directory.

Read [references/selection-rubric.md](references/selection-rubric.md). Before every cull, read and follow [references/style-reference-sources.md](references/style-reference-sources.md) and [references/reference-calibration-schema.md](references/reference-calibration-schema.md). Use `watch` for scene-aware video evidence. Use `video-use` only for later exact-frame or creative editing.

## Workflow

1. Account for every canonical source in `reference-source-map.json`. Attempt every applicable automatic source; mark non-applicable manual sources as not selected with a concrete `skip_reason`. Record failures honestly rather than replacing visible evidence with page text or remembered style.
2. If manual enhancement was selected and the user confirmed readiness, inspect only the single selected source in the user's visible browser. Record visible samples and limitations. A failed or protected source is skipped honestly; never request authentication data or bypass protection.
3. Record `reference-calibration.json` using [references/reference-calibration-schema.md](references/reference-calibration-schema.md): per-media automatic results, one optional manual mode/source, access time, discovery path, actual visible samples, limitations/failures, observed patterns, and applied selection rules.
4. Synthesize cross-source patterns only from actual visible samples repeated across at least two suitable sources. Keep long-term standards, optional manual trend/author signals, and single-author signatures separate. Likes, views, ratings, and ranking are discovery signals only.
5. Run `python3 scripts/validate_reference_calibration.py --input <reference-calibration.json>`. Continue on `ready-automatic`, `ready-manual-enhanced`, or an explicitly authorized static result. Exit `3` means at least one requested media gate remains partial/unavailable and screening must pause for the user's static-fallback decision; exit `2` means repair the evidence log before culling.
6. Inventory read-only: paths, type, dimensions or duration, capture time, corruption, and duplicate groups.
7. Inspect representative frames and useful long-video intervals.
8. Apply the validated reference calibration plus aesthetic/story and relationship/memory channels. Relationship value may rescue imperfect media when the interaction remains discernible.
9. Run the natural first-pass classification as `select`, `review`, `memory`, or `excluded`. The highest principle is to retain meaningful, high-quality, usable, and non-redundant material. Do not ask about percentages in the opening prompt and never treat a percentage as a quota.
10. Apply the soft second-pass guardrails separately by media kind. The 10% primary and 25% review ratios are soft second-pass triggers, not hard caps: above either trigger, remove weak alternatives, dead air, and redundancy first. `select` overflow moves to `review`; `review` overflow moves to `not_selected`, never to `memory` or `excluded`.
11. For photos, divide deduplicated `select` and `review` candidate counts by the deduplicated photo candidate count; RAW+JPEG pairs and byte-identical files count once. For videos, video ratios use duration, not file count: divide the union of selected/review intervals by the total duration of all deduplicated readable source videos, and give `select` priority when intervals overlap.
12. Meaningful, high-quality, usable, non-redundant items may remain above 10%/25% automatically when `selection_evidence` records the reason. Relationship progression, distinct story beats, rare events, and complete meaningful actions/dialogue/emotional arcs are valid evidence. There is no secondary cap for genuine exceptions; report them. Collections with at most 60 seconds of total readable video skip percentage compression, and very small photo sets may keep at least one deserved primary item.
13. Choose retained representatives with the active category profile and validated reference calibration. For posed portraits or groups, prefer visible unobstructed faces, open eyes, natural or engaging expressions, suitable camera-facing gaze, composition, light, focus, and timing. For candid, documentary, or family interaction, let emotion, relationship, interaction, and story beat outweigh direct gaze when stronger. Popularity metrics never replace judgment.
14. Create a UTF-8 CSV manifest with `source_path,decision,reason,start_time,end_time`. Use one row per useful video interval. For deterministic second-pass handling, add `candidate_id,similarity_group,relationship_progression,story_beat,representative_score,capture_style,selection_evidence`; blank values remain valid. Optionally add `paired_jpeg_path` for a known RAW+JPEG pair; otherwise same-stem `.jpg`/`.jpeg` is detected automatically.
15. Run `scripts/build_review_set.py --manifest <csv> --output <dir> --mode link|copy --video-delivery auto|timecodes|clips [--select-ceiling 0.10] [--review-ceiling 0.25] [--short-video-seconds 60]`. Prefer `auto`: copy mode exports lightweight clips, link mode keeps timecodes. The script measures readable video duration, prints a rough non-zero storage estimate, and records first-pass, final, and quality-exception ratios.
16. Inspect `generation_status`, `review_asset_kind`, and `generation_detail` in `筛选清单.csv`; inspect `未入选清单.csv` separately from `排除清单.csv`. Verify counts, mappings, playable clips, links, sources, reasons, duration denominators, and every over-trigger exception. Exit status `3` means the review set exists but one or more derivatives failed; do not present it as fully successful.
17. Report uncertainty instead of rejecting guesses. Map every review file back to its high-quality original and tell the user to use originals for final editing.

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
- `memory` is independently justified sentimental material, never overflow storage used to evade the soft selection triggers. Distinct relationship beats may be protected; an entire near-identical burst is not protected by default.
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

## Continue with Shining Cut

After the review set is delivered and verified, briefly offer `$shining-cut` as the recommended next step for turning the selected videos into a reference-calibrated script, initial cut, and optional fine cut. Do not start editing without the user's confirmation. Shining Cut must use the high-quality originals through this Skill's manifest mappings, not the lightweight review derivatives.
