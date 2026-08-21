# Personal Media Selection Rubric

Use this rubric for conservative first-pass decisions. Scores support judgment; they do not replace it.

## Technical viability gate

Assess what remains after reasonable correction, not hypothetical restoration.

### Photos

- **Viable:** the subject, action, expression, or meaningful context is discernible after plausible crop, exposure, and color correction.
- **Reviewable:** mild blur, noise, imperfect exposure, awkward framing, or partial obstruction remains, but the moment can still be understood.
- **Unusable:** corrupt or unreadable file; effectively blank frame; no meaningful subject or relationship can be recognized after reasonable correction.

### Videos

- **Viable:** the meaningful action can be followed and the shot has enough stable visual information to edit.
- **Stabilizable:** standard editor stabilization with a moderate crop could preserve the subject and action without strong warping, pulsing edges, or an unusably tight frame. Do not assume AI reconstruction.
- **Shaky but meaningful:** faces, interaction, or the key event remain recognizable. Normal footage usually goes to `review`; relationship-rich footage must stay in `review` even when it is unlikely to stabilize cleanly.
- **Visually unrecognizable:** continuous motion prevents recognition of any subject or event. Use `memory` only when sentimental significance is known; otherwise use `excluded`.

Do not reject a clip from one bad frame. Sample the beginning, middle, end, scene changes, and audio- or transcript-signaled moments.

## Aesthetic and story channel (100 points)

| Factor | Weight | What earns value |
|---|---:|---|
| Composition | 15 | clear subject, intentional framing, depth, balance, useful negative space |
| Light and color | 15 | readable exposure, coherent color, atmosphere, recoverable highlights and shadows |
| Emotion | 20 | expression, gesture, tension, delight, tenderness, surprise, calm |
| Narrative function | 20 | establishes place, advances action, reveals character, connects scenes, provides payoff |
| Uniqueness | 10 | rare viewpoint, unrepeatable event, distinctive detail |
| Authenticity | 10 | natural behavior, lived-in detail, absence of empty posing or generic filler |
| Technical quality | 10 | focus, resolution, sound, stability, duration, editability |

- **75–100:** strong `select` candidate when technically viable.
- **45–74:** `review`; the user decides whether it serves the edit.
- **Below 45:** during the normal first pass, do not use a low score alone to mark usable material `excluded`. If conditional overflow reduction later omits that usable item from the shortlist, use `not_selected`; reserve `excluded` for confidently unusable or corrupt media without relationship value.

## Relationship and memory channel (20 points)

Score each dimension from 0–5:

| Dimension | Evidence |
|---|---|
| Relationship clarity | touch, gaze, shared action, care, humor, comfort, reunion, farewell |
| Emotional truth | spontaneous expression, vulnerability, affection, family rhythm, friendship chemistry |
| Irreplaceability | deceased or distant relative, rare gathering, first or last occasion, childhood change, milestone |
| Memory context | recognizable place, ritual, object, voice, phrase, or event meaningful to the people involved |

- **14–20:** may enter `select` despite ordinary composition or minor technical flaws, if the moment remains understandable.
- **8–13:** relationship evidence strongly supports `review`, but a near-identical burst still needs distinct-beat comparison if overflow reduction triggers.
- **1–7:** supporting evidence, not an automatic rescue.
- **Known sentimental significance but visually unusable:** `memory`, never normal `select`.

## Duplicate policy

Group exact and near-duplicates during the normal first pass. Recommend the strongest representative for `select`; use `review` for genuinely useful alternatives, not every technically usable frame. For byte-identical files, prefer the canonical original with the richest metadata and highest valid resolution; if still tied, use a stable path order. Repetition alone never makes a usable item `excluded`; a usable item omitted from the shortlist is `not_selected`.

## Conditional backup overflow reduction

After the normal first pass, calculate the review ratio against the deduplicated unique candidate set. A RAW+JPEG pair counts once, as does a group of byte-identical files. The default ceiling is 20%; an explicit user-supplied ceiling may replace it.

- The percentage is a ceiling, never a quota or target. If the first-pass review ratio is at or below the ceiling, do nothing: neither prune good review items nor add weak ones to fill the percentage.
- Only when the ratio is above the ceiling, run a second reduction pass until the ratio is at or below it. This is a post-classification check, not another opening question.
- Remove unchanged redundancy first. Compare scene, identities, people count, expressions, pose or action, framing, and story beat. An ordinary same-scene/person burst normally keeps no more than 1–2 truly distinct `review` alternatives in addition to any deserved `select` representative.
- An irreplaceable family or friend progression may keep 3–5 `review` or independently justified `memory` frames only when they carry genuinely different setup, peak, resolution, or relationship beats. The global review ceiling still wins when the collection is too small to hold that many review frames. Never retain an entire burst by default, and never relabel overflow as `memory`.
- When a global trim is still required, use the active category profile and the calibrated visual/story standard. Popularity counts never substitute for judgment.

### Representative evidence

- **Posed portrait or group:** prefer visible and unobstructed faces, open eyes, natural or engaging expression, suitable camera-facing gaze, stronger composition and light, focus, and timing.
- **Candid, documentary, family, or friendship:** do not mechanically reward direct camera gaze. Prefer the frame with stronger interaction, emotion, relationship clarity, authenticity, and story beat.

For deterministic script handling, provide a stable `candidate_id` for known RAW pairs or duplicates when useful, a `similarity_group` for burst membership, `relationship_progression=true` only for irreplaceable progressions, a concrete `story_beat`, and a numeric `representative_score` derived from this rubric and the active category profile. `capture_style` and `selection_evidence` preserve why the score was assigned. The script also detects same-stem RAW+JPEG pairs and byte-identical files when these fields are absent.

## Long-video policy

Add one manifest row per useful interval with precise `start_time`, `end_time`, and reason.

- **Link + timecodes:** link the whole original once. When intervals differ, place the link only in the highest-priority included folder: `select`, then `review`, then `memory`. Keep every interval in the manifest.
- **Copy + timecodes:** copy no whole video. Keep the original path, category, reason, and precise interval in the manifest and report.
- **Clips:** create a new H.264/AAC MP4 review derivative for every timed `select`, `review`, or `memory` interval. A memory derivative stays in `03_纪念留档` and is not a normal-edit recommendation. Never create media for `excluded` rows.
- Cap landscape derivatives at 1280×720 and portrait derivatives at 720×1280 while preserving aspect ratio. Never upscale a source already within those bounds.
- Treat HDR/HLG, display rotation, and variable frame rate as technical-risk signals. Validate a short sample for color, orientation, playability, and audio/video duration drift before the full interval.
- A derivative failure must be explicit: retain the source/timecode mapping, set the result to `not-generated` / `failed`, give an actionable `ffmpeg`/`ffprobe` hint, and never fall back to copying the full high-bitrate source.

## Lightweight photo-copy policy

- Keep the safe copy behavior for directly reviewable non-RAW photos such as JPEG, HEIC, and PNG.
- For an included RAW, prefer `paired_jpeg_path` or a same-stem `.jpg`/`.jpeg`; record the RAW original and the JPEG used for review.
- When no pair exists, generate a quality-85 JPEG review copy with an available converter. The converter should handle orientation and produce recognizable color suitable for human re-screening; spot-check generated results.
- If a converter is unavailable or fails, never copy the large RAW as a disguised fallback and never claim success. Keep the original mapping, mark the review item ungenerated, and report the dependency or format-support problem.
- Estimate review-set storage before writing. The estimate is approximate and not zero, but avoiding full RAW and whole high-bitrate video copies should substantially reduce review-directory size.

## Decision contract

| Decision | Meaning |
|---|---|
| `select` | strongest first-pass recommendations; still subject to user approval |
| `review` | usable and genuinely useful alternative, uncertainty, repairable material, or a distinct relationship beat for user re-screening |
| `memory` | independently justified sentimental record not recommended for normal editing; never overflow storage |
| `not_selected` | usable but not shortlisted; no media derivative, retain original path and reason in `未入选清单.csv` |
| `excluded` | confidently unusable, corrupt, or unrecognizable non-sentimental material; record only in `排除清单.csv`, never delete |
