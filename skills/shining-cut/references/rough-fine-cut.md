# Rough cut, fine cut, and QA

Use the bundled `video-use` Skill as the editing runtime and preserve its production-correctness rules. Prefer the registered Skill; otherwise resolve the sibling `../video-use/` directory from Shining Cut's installed location. Its `SKILL.md`, `helpers/`, and `pyproject.toml` must remain together. Do not assume a command, environment, or dependency is available until preflight succeeds.

## Rough cut

After the second confirmation:

1. Translate the approved blueprint into an EDL with absolute original paths and source ranges.
2. Use primary footage for the main timeline and backup footage only for replacement or coverage. Never edit from review proxies and never use excluded material.
3. For spoken material, keep word-level verbatim transcript timing, word-boundary cuts, edge padding, transcript caching, and output-timeline subtitle offsets required by `video-use`.
4. For every cut, consider both image and sound. Add short audio fades at segment boundaries and place subtitles last in the compositing chain as required by `video-use`.
5. Render a new, playable rough cut without overwriting any source or earlier accepted output.
6. Apply the blueprint's primary grade during per-segment extraction: correct SDR/Log/HDR handling, exposure, white balance, basic shot matching, and the approved restrained topic-aware look. Never show untransformed Log, broken HDR, or obvious color casts as a reviewable rough cut.
7. Verify decoding, expected duration, dimensions, aspect ratio, audio presence, audio/video sync, source availability, basic joins, output color space/tags, and primary-grade continuity before presenting it.

Keep working artifacts under the confirmed project's `edit/` area. Use versioned names whenever a target already exists. A practical artifact set is `edl.json`, `rough-cut.mp4`, verification frames or contact sheets, and the existing calibration, source map, blueprint, and storyboard.

## Automatic rough-cut review

Review the rendered rough cut itself, not only the EDL or source clips.

- Use `watch` on the local rough cut for overall structure and scene-aware evidence when its preflight succeeds.
- Use `video-use` timeline inspection around actual cut boundaries for flashes, discontinuities, waveform spikes, overlay timing, and subtitle obstruction.
- Sample the opening, ending, and representative points across every section.
- Compare actual runtime, aspect ratio, structure, and pacing with the approved blueprint and calibration rules.
- Check repetition, awkward gaps, rushed beats, missing coverage, sound balance, dialogue clarity, captions, transitions, reframing, stabilization, and color continuity.
- Verify the primary grade and identify whether optional secondary grading would materially improve skin, sky, local highlights or shadows, subject separation, or a requested look. Record the proposal but do not apply it yet.

Fix only technical defects needed to make the rough cut reviewable. Editorial changes belong in the fine-cut plan and wait for the third confirmation.

## Timecoded fine-cut plan

Write `fine-cut-plan.md` as a change list, not a replacement script. Every row should contain:

- current rough-cut time range;
- observed issue and evidence;
- proposed trim, replacement, reorder, sound, caption, transition, framing, stabilization, or color change;
- affected original interval or output layer;
- expected effect on pacing, clarity, emotion, and total runtime;
- the approved blueprint or reference rule supporting the change.

Include a concise summary of the resulting expected duration and any remaining limitations. Present the playable rough cut and this plan together for the third confirmation defined in `interaction-contract.md`.

## Execute the confirmed choice

- **Keep rough cut:** do not apply editorial fine-cut changes. Run delivery QA on the accepted rough cut and label it accordingly.
- **Apply recommendation:** execute the recorded fine-cut list exactly, making only necessary technical corrections discovered during render validation. Retain the primary grade unless the user also selected secondary grading.
- **User revision:** incorporate the user's one-batch changes into the list, preserve timecode traceability, then execute without another routine confirmation.

Fine cut does not imply secondary grading. Keep the primary grade by default. Only an explicit secondary-grade choice authorizes masks, tracked/local corrections, targeted skin or sky work, subject separation, selective hue/luminance shaping, or a stronger creative look. Record the selected color option in `fine-cut-plan.md`.

Do not use later QA as permission for unapproved creative changes. If validation exposes a change that materially alters the approved story or source choice, report it as a blocker.

## Final QA and delivery

Verify the actual delivered file with `ffprobe`, playback/frame evidence, and targeted timeline inspection. Check:

- the file decodes and the expected duration, resolution, frame rate, and aspect ratio are present;
- audio/video sync, channel presence, boundary fades, and mix levels are acceptable;
- subtitles are readable, timed to the output, and not hidden by overlays;
- no missing media, unintended black frames, broken transitions, orientation errors, or obvious color discontinuities remain;
- the accepted primary grade remains intact when secondary grading was declined, or the confirmed secondary-grade operations are present when selected;
- output color space and transfer tags are correct for the delivery target and do not produce an unintended SDR/HDR appearance shift;
- every used interval maps to a high-quality original path and no source was moved, overwritten, or deleted;
- the final filename is new or versioned and all known limitations are disclosed.

Deliver the final or accepted rough-cut video together with `reference-calibration.md`, `source-map.csv`, `script-blueprint.md`, `storyboard.md`, the executed EDL, `fine-cut-plan.md` when applicable, and verification evidence. Claim only the checks actually run.
