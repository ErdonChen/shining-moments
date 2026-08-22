# Script and storyboard blueprint

Generate the blueprint automatically after the first confirmation and successful reference calibration. It is a reviewable editing strategy, not permission to render the cut.

## Source inventory and original mapping

Inventory readable video with `ffprobe` or equivalent verified metadata. Measure usable duration, not file count. For every candidate interval retain:

- an absolute high-quality original path;
- source start and end timecodes;
- primary or backup role and the screening evidence;
- resolution, frame rate, orientation, audio presence, and relevant decode limits;
- any review derivative or link used for discovery, kept separate from the original used for editing.

For Shining Moments inputs, use `select` intervals as primary and `review` intervals as backup. Do not silently add `memory` or `not_selected`; never add `excluded`. A proxy, thumbnail, generated review clip, or low-resolution copy is not an editing master.

Mixed directories default to video only. Add photos only when the user explicitly requested them, and map each photo to its high-quality original.

## Recommendations

Recommend the final runtime from usable video duration, non-duplicate places and events, story coverage, primary/backup quality, calibrated reference pacing, target platform, and aspect ratio. Do not derive runtime from file count or force a social-media length without evidence.

The blueprint must include:

1. source inventory summary and total usable video duration;
2. recommended final runtime, aspect ratio, and publishing destination, each with a reason;
3. one-sentence theme and overall emotional direction;
4. opening, development, major beats, emotional peak, and ending;
5. expected duration of every section;
6. candidate original intervals with accurate source timecodes and backups;
7. representative source frames forming a storyboard preview;
8. music, ambience, dialogue, voiceover, silence, caption, and title plan;
9. transition, pacing, stabilization, reframing, and primary-grade intentions;
10. the specific transferable reference rule supporting each non-obvious choice.

## Primary-grade plan

The blueprint must propose a primary grade that will be visible in the rough cut. Detect ordinary SDR, Log, HLG/PQ HDR, mixed cameras, and mixed color spaces from metadata plus representative decoded frames. Do not infer a profile from a filename or apply an unverified LUT.

Separate technical normalization from creative direction: establish the correct transform, exposure, white balance, and basic shot matching first, then apply a restrained topic-aware base look. Protect skies and highlight detail for landscape/travel, prioritize skin accuracy for portrait/family/friends, favor natural continuity for Vlog/documentary, and preserve believable darkness while controlling noise and color casts for night footage. When profiles are mixed, normalize per clip before applying the shared base look.

Show the proposed base look and its reason in the blueprint. Reference videos may inform direction, but their LUTs or values must not be copied. This is the primary grade approved with the second confirmation. Secondary grading is not part of the blueprint default and remains optional after rough-cut review.

## Timecoded storyboard

Use a table with one row per planned beat. Include:

- planned output range;
- beat and narrative purpose;
- original path and source range;
- primary interval and backup interval;
- representative frame path or contact-sheet reference;
- sound treatment and any spoken-content boundary;
- caption, title, transition, color, or reframing treatment;
- reference-calibration rule and the reason it transfers.

Keep source and output timecodes distinct. If dialogue or narration is cut, use the downstream `video-use` word-level transcript and word-boundary rules; do not manufacture transcript precision.

## Review artifacts

Before the second confirmation, write or update:

- `source-map.csv` for original-path and interval mapping;
- `script-blueprint.md` for the narrative, recommendations, and edit strategy;
- `storyboard.md` plus representative frame/contact-sheet assets;
- `reference-calibration.md` from the preceding stage.

Present these artifacts and the complete blueprint in one batch, then ask the second centralized confirmation from `interaction-contract.md`. Do not create a rendered cut before approval. After approval, translate the confirmed timecoded plan into the actual downstream EDL and keep both versions traceable.
