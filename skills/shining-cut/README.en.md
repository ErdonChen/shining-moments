# Shining Cut

English | [简体中文](README.md)

Shining Cut is an intelligent video-editing Skill, recommended for use with Shining Moments. It extracts pacing, structure, shot language, sound, and color direction from relevant reference videos, then maps those patterns onto the user's screened footage.

## Reference modes

- **Automatic references**: Google Videos and Wikimedia Commons Videos.
- **Enhanced references (optional)**: YouTube or Bilibili; the user may also submit a reference-video URL.

## Three-step workflow

1. **Confirm the topic and reference target**: read the screened footage and confirm the topic, keywords, and reference plan.
2. **Script and initial cut**: create the editing script, timecoded storyboard, and primary-grade plan; render the initial cut after user approval.
3. **Fine cut (optional)**: review the initial cut and propose a change list; when requested, complete the fine cut, optional secondary grade, and final QA.

Shining Cut can read Shining Moments manifests and original-media mappings, or accept footage screened through another workflow. For unscreened source media, it recommends using Shining Moments first.

Every edit maps back to high-quality originals. Original media is never moved, overwritten, or deleted.

## Bundled runtimes

- **Watch** provides actual decoding, timestamped frames, and caption/transcript evidence for reference videos and local renders.
- **Video Use** provides word-level transcription, EDL execution, rendering, subtitle/animation compositing, and cut-boundary self-evaluation.

When the complete `Shining-Moments-Cut` bundle is installed, both Skills sit next to Shining Cut. Shining Cut's approved blueprint also satisfies Video Use's strategy-confirmation requirement, so the workflow does not ask for a duplicate routine edit-strategy approval.
