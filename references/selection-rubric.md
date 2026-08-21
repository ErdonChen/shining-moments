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
- **Below 45:** exclude only when it also lacks relationship value and is confidently unusable or redundant filler.

## Relationship and memory channel (20 points)

Score each dimension from 0–5:

| Dimension | Evidence |
|---|---|
| Relationship clarity | touch, gaze, shared action, care, humor, comfort, reunion, farewell |
| Emotional truth | spontaneous expression, vulnerability, affection, family rhythm, friendship chemistry |
| Irreplaceability | deceased or distant relative, rare gathering, first or last occasion, childhood change, milestone |
| Memory context | recognizable place, ritual, object, voice, phrase, or event meaningful to the people involved |

- **14–20:** may enter `select` despite ordinary composition or minor technical flaws, if the moment remains understandable.
- **8–13:** keep in `review`; aesthetic scoring cannot remove it.
- **1–7:** supporting evidence, not an automatic rescue.
- **Known sentimental significance but visually unusable:** `memory`, never normal `select`.

## Duplicate policy

Group exact and near-duplicates. Recommend the strongest representative for `select`, but put every other usable member in `review` so the user can compare expressions, gestures, and timing. For byte-identical files, prefer the canonical original with the richest metadata and highest valid resolution; if still tied, use a stable path order. Never exclude a usable item only because it is repetitive.

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
| `review` | usable, uncertain, duplicate, repairable, or relationship-protected media for user re-screening |
| `memory` | sentimental record not recommended for normal editing |
| `excluded` | confidently unusable non-sentimental material; record only, never delete |
