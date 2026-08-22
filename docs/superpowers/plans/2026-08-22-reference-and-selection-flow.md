# Shining Moments Reference And Selection Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved automatic/manual reference flow and evidence-backed photo-count/video-duration selection guardrails.

**Architecture:** Bump the reference catalog/evidence schema so automatic, challenge-assisted, login-assisted, and custom visible-browser evidence are explicit and validated per media kind. Replace the single hard review-count reducer with a two-media guardrail engine: photo ratios use deduplicated candidates, video ratios use interval-union duration, and quality evidence may retain justified overflow.

**Tech Stack:** Markdown/YAML Skill instructions, JSON source catalog, Python 3 standard library, `unittest`, ffprobe/ffmpeg integration already present in the repository.

**Spec:** `docs/superpowers/specs/2026-08-22-reference-and-selection-flow-design.md`

## Global Constraints

- Automatic sources are fixed by media kind; the user does not select a subset.
- Photo and video reference readiness are evaluated independently with two visible sources per requested kind.
- Users complete challenges and logins in a visible browser; authentication secrets are never handled.
- Photo 10%/25% and video-duration 10%/25% are second-review triggers, not hard caps.
- High-quality, meaningful, non-redundant overflow stays when concrete evidence is recorded.
- Originals remain read-only and GitHub remains untouched.

---

### Task 1: Reference catalog and calibration validator

**Files:**
- Modify: `references/reference-source-map.json`
- Modify: `references/reference-calibration-schema.md`
- Modify: `scripts/validate_reference_calibration.py`
- Test: `tests/test_skill_workflow.py`
- Test: `tests/test_validate_reference_calibration.py`

**Interfaces:**
- Consumes: material type, requested media kinds, fixed automatic catalog routes, optional manual mode and selected source.
- Produces: per-media readiness and `ready-automatic`, `ready-manual-enhanced`, `paused-partial`, `paused-unavailable`, or static-authorized results.

- [ ] Add failing catalog tests asserting automatic photo/video pools and challenge/login pools.
- [ ] Add failing validator tests for hybrid evidence, separate photo/video gates, Google preview/playback evidence, Pexels mixed-session selection, custom source records, and sensitive-field rejection.
- [ ] Run `python3 -m unittest tests.test_skill_workflow tests.test_validate_reference_calibration -v`; verify failures name the old catalog/schema behavior.
- [ ] Bump the catalog and calibration payload to schema version 3 and implement fixed automatic routing plus explicit manual modes.
- [ ] Implement per-media visible-source counts and hybrid readiness without weakening static-fallback behavior.
- [ ] Re-run the two test modules and make them pass.

### Task 2: Photo-count and video-duration guardrail engine

**Files:**
- Modify: `scripts/build_review_set.py`
- Modify: `references/selection-rubric.md`
- Test: `tests/test_build_review_set.py`

**Interfaces:**
- Consumes: normalized manifest rows, representative scores, selection evidence, similarity/story metadata, ffprobe-readable source durations, and configured select/review trigger ratios.
- Produces: updated decisions, interval trims where explicitly supplied, evidence-backed retained-overflow records, and separate photo/video statistics for reporting.

- [ ] Add failing photo tests for 10% select and 25% review triggers, demotion order, minimum-one behavior, and evidence-backed soft-limit retention.
- [ ] Add failing video tests using deterministic fake ffprobe output for duration denominators, overlapping-interval unions, 60-second collection bypass, complete-interval exception, and soft-limit retention.
- [ ] Run the targeted tests and verify they fail because the current code has only a hard review-count ceiling.
- [ ] Add `--select-ceiling 0.10`, change `--review-ceiling` default to `0.25`, and preserve explicit overrides.
- [ ] Implement media-partitioned statistics, deduplicated photo counts, deduplicated source-video durations, interval-union duration, and quality-evidence exceptions.
- [ ] Implement select-to-review then review-to-not-selected demotion without using `memory` or `excluded` as overflow.
- [ ] Re-run all build-review-set tests and make them pass.

### Task 3: Skill workflow and bilingual documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `references/style-reference-sources.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Test: `tests/test_skill_workflow.py`

**Interfaces:**
- Consumes: the schema/catalog and guardrail behavior from Tasks 1-2.
- Produces: one coherent user-facing workflow in Chinese and English plus concise agent instructions.

- [ ] Add or adjust workflow tests that exercise catalog/schema behavior rather than exact prose.
- [ ] Run the workflow tests and verify failure against the old source-selection/manual-enhancement sequence.
- [ ] Rewrite the opening workflow to ask topic, media kinds, optional manual mode, then link/copy.
- [ ] Document automatic, challenge-assisted, login-assisted, and custom URL handling plus one-source recommendation behavior.
- [ ] Document photo-count and video-duration soft guardrails and exception evidence.
- [ ] Re-run workflow and validator tests.

### Task 4: Full verification, installed-copy synchronization, and local commit

**Files:**
- Synchronize: `/Users/iceberry/.codex/skills/shining-moments`
- Verify: all repository and installed Skill files

**Interfaces:**
- Consumes: completed source tree.
- Produces: tested source and installed trees with byte-for-byte parity and one local Git commit.

- [ ] Run `python3 -m unittest discover -s tests -v` and require zero failures.
- [ ] Run `git diff --check` and the Skill Creator `quick_validate.py` against the source tree.
- [ ] Synchronize only tracked Skill files to the installed directory; do not remove unrelated user files.
- [ ] Compare source and installed files byte-for-byte and run `quick_validate.py` against the installed tree.
- [ ] Inspect `git diff --stat`, `git diff`, and `git status --short`; verify scope against the approved spec.
- [ ] Create one local commit describing the reference-flow and guardrail update. Do not push.
