# Reference calibration

Reference calibration is evidence gathering for editorial decisions. Automatic public-reference discovery always attempts both Google Videos and Wikimedia Commons Videos, even when the user supplies a main reference. Optional enhancement is off by default and may add exactly one platform: YouTube or Bilibili.

## Discovery and selection

Build search concepts from confirmed keywords, topic, location, season, people or relationship, event, mood, and intended final form. Attempt Google Videos and Wikimedia Commons Videos as the fixed public, no-login automatic pool. Record access and evidence separately for both; do not invent a private API or account capability.

Create a candidate table before choosing references. Rank candidates in this order:

1. footage relevance: location, topic, season, relationship, and event;
2. the platform's visible ranking or result order;
3. visible views, likes, and interaction signals;
4. suitability for extracting transferable editing rules.

Popularity is a discovery signal, not proof of editing quality. Record when a metric is unavailable, ambiguous, or likely stale.

If the user supplied a reference URL, treat it as the intended main reference. It keeps that role only after playable evidence is obtained. If it cannot be accessed, pause for an accessible alternative or explicit permission to replace it. Without a user reference, select the highest-ranked playable candidate as main. Select at most two auxiliary references that add useful contrast or corroboration rather than repeating the main reference.

## Evidence gate

A reference counts only when video actually decodes or visible playback time advances in this run.

- For a public URL or local file, use the bundled `watch` Skill and follow its preflight and evidence limits. Prefer the registered Skill; otherwise resolve the sibling `../watch/` directory from Shining Cut's installed location and keep its `SKILL.md` with `scripts/`.
- For an enhanced source that requires login, the user authenticates in their own visible browser. Inspect only visible playback in that same user-controlled session; never extract or pass credentials, verification codes, cookies, API keys, or other authentication secrets to `watch` or another process.
- Sample the opening, middle, ending, and clearly distinct visual beats. Increase coverage when pacing, transitions, narrative, dialogue, music, or sound design materially affects the analysis.
- A thumbnail, poster frame, search result, page shell, title, transcript alone, or remembered platform style is not playback evidence.

At least one playable main reference is required. Auxiliary references are optional up to a maximum of two. If automatic discovery produces no playable evidence, report the attempted discovery paths and failures and pause before the blueprint; do not replace current observation with static aesthetic knowledge.

## Analysis dimensions

For every selected reference, record evidence-backed observations about:

- how the opening establishes place, subject, or question;
- story and section structure;
- approximate shot-hold pattern and pacing changes;
- wide, medium, close-up, detail, and movement ordering;
- transition types and frequency;
- music, ambience, dialogue, voiceover, and silence;
- captions, titles, and location markers;
- emotional peak and ending behavior;
- which patterns can transfer to the user's footage and where they would apply.

Separate direct observations from inferences. Do not copy a reference's exact shot sequence, distinctive text, graphics, narration, music, or other protected expression. Synthesize rules such as pacing ranges, structural functions, coverage patterns, and sound relationships.

## Calibration record

Write `reference-calibration.md` in the confirmed project output area with these sections:

1. confirmed keywords, topic, final form, and enhancement mode;
2. discovery queries and access time;
3. candidate table with URL, platform, visible ranking/metrics, playability status, and selection decision;
4. selected main reference and up to two auxiliaries;
5. sampled intervals and the evidence obtained from each;
6. per-reference observations;
7. cross-reference transferable rules;
8. rejected signatures that must not be copied;
9. limitations, failed sources, and uncertainty.

Every blueprint choice attributed to a reference must point back to an observed rule in this record.
