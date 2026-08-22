---
name: shining-cut
description: Plan and execute reference-calibrated edits from already-screened footage, producing a timecoded script and storyboard, rough cut, fine-cut plan, and verified final. Use for deliberate end-to-end video editing; do not use for merely watching or summarizing a video, simple transcoding or format conversion, or unscreened-media culling.
---

# Shining Cut

Turn already-screened footage into a reference-calibrated edit while keeping every decision traceable to high-quality originals.

## Start with the readiness gate

1. Inspect the supplied paths, reports, and manifests read-only. Do not assume the user ran Shining Moments.
2. Proceed only when the footage is already screened and the included material can be distinguished from rejected material. If it is unscreened, pause before reference research or editing and suggest `$shining-moments`. Do not silently perform culling inside this skill.
3. When the input is a Shining Moments review set, resolve its manifest and reports back to `source_path` and source timecodes. Treat `select` as primary material and `review` as backup. Do not silently promote `memory` or `not_selected`, and never use `excluded`.
4. Before speaking to the user, read [references/interaction-contract.md](references/interaction-contract.md). Keep the normal workflow to its three centralized confirmations; ask an extra question only for a genuine execution blocker.

## Run the workflow

1. **First confirmation — material and reference plan.** Present one prefilled request covering screening status and paths, content/form, extracted keywords, optional reference enhancement, optional user reference link, and the proposed project output location.
2. **Reference calibration.** Read and follow [references/reference-calibration.md](references/reference-calibration.md). Automatic public-reference discovery through Google Videos and Wikimedia Commons Videos always runs. Optional enhancement defaults off and, when enabled, is exactly one of YouTube or Bilibili. Select one main reference and at most two auxiliaries using playable evidence; extract transferable rules rather than copying a work.
3. **Script and storyboard blueprint.** Read [references/script-blueprint.md](references/script-blueprint.md). Inventory usable video duration, recommend duration/aspect/platform, and produce a timecoded narrative, original-file mapping, representative storyboard, sound/subtitle plan, primary-grade plan, and reference rationale. Ask for the second centralized confirmation only after the complete blueprint is reviewable.
4. **Rough cut.** After approval, read and follow [references/rough-fine-cut.md](references/rough-fine-cut.md). Build a playable rough cut from mapped originals, apply the approved primary grade, and perform basic technical checks.
5. **Automatic rough-cut review.** Watch the rendered rough cut, inspect exact cut boundaries where needed, and create a timecoded fine-cut change list rather than rewriting the full script.
6. **Third confirmation — fine-cut decision.** Offer exactly: keep the rough cut, apply the recommended fine cut, or revise the fine-cut list once and then execute it. Default to retaining the rough cut's primary grade; offer secondary grading only as an explicit optional choice.
7. **Fine cut, QA, and delivery.** Execute the confirmed choice, run secondary grading only when the user selected it, verify the actual output, and preserve the reference record, script, storyboard, timecodes, EDL, and original mapping beside the deliverable.

## Use real downstream capabilities

- Use the installed `watch` skill for public video URLs or local rendered files when it can provide decoded frames and timestamped evidence. Follow its own preflight. It does not authenticate to platform accounts or accept browser cookies.
- Use the installed `video-use` skill for actual editing. Follow its runtime setup and production-correctness rules. The confirmed Shining Cut blueprint is the required plain-English strategy approval; do not introduce another ordinary strategy-confirmation round.
- For a YouTube or Bilibili enhancement that genuinely needs login, let the user authenticate in their own visible browser and inspect only media visible there. Never ask for, receive, store, export, or reuse a username, password, verification code, cookie, API key, or session secret. If a downstream transcript service needs an API key, ask the user to configure it outside Shining Cut or continue with evidence that does not require it.
- If either required downstream skill or its runtime is unavailable, report the concrete preflight failure and pause. Do not fabricate a tool, playback result, transcript, reference observation, or edit.

## Preserve sources and evidence

- Default to video only. Ignore photos in mixed folders unless the user explicitly asks to add them.
- Never move, overwrite, or delete original media. Create new, versioned outputs under the confirmed project output location.
- Edit from high-quality originals, not review proxies, thumbnails, or low-resolution derivatives. Every used interval must map to an absolute original path and source time range.
- Never use page text, metadata, a search snippet, or a thumbnail as proof that a reference was watched. Record access limits honestly.
- Do not claim a rough cut, final render, playback check, or QA pass unless the corresponding artifact was actually produced and verified in this run.
