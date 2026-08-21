# Reference Calibration Evidence

Choose the material type, route its relevant sources from [reference-source-map.json](reference-source-map.json), and only then create `reference-calibration.json` before inventory or culling. Probe endpoints from that routed set. The file is an audit trail for live observation and the connectivity decision, not a cache of permanent style claims.

## Readiness branches

| Connectivity | User authorization | `calibration_mode` | Result |
|---|---|---|---|
| reachable | not needed | `live` | Visit and account for all canonical sources; validate to `ready-live`. |
| unavailable | absent or refused | `paused` | Show the required notice, ask once, and pause. Validator exits `3`. |
| unavailable | explicit | `static-authorized` | Record the user's confirmation; make no live or recent-trend claims. |

The required notice is:

> 当前无法查阅参考网站，因此不能获得实时参考/近期趋势。

Then ask whether the user agrees to continue with existing static aesthetic knowledge or prior impressions. Silence is not agreement. Do not inventory, inspect, classify, link, copy, or export media while the state is `paused`.

## Top-level fields

```json
{
  "schema_version": 1,
  "material_type": "vlog-event",
  "connectivity_check": {
    "status": "reachable",
    "checked_at": "2026-08-21T14:25:00+08:00",
    "probe_targets": [
      "https://vimeo.com/channels/staffpicks",
      "https://www.youtube.com/"
    ],
    "detail": "Both public endpoints responded from the current environment"
  },
  "calibration_mode": "live",
  "static_fallback_authorized": false,
  "sources": [],
  "calibration_summary": {}
}
```

Use ISO-8601 timestamps. Do not record credentials, cookies, tokens, or other secrets.

## Live source record

Include exactly one record for every source in [reference-source-map.json](reference-source-map.json). Required sources are `relevant`. Every other source is either researched as `relevant` or marked `skipped` with a project-specific reason.

```json
{
  "source_id": "vimeo-staff-picks",
  "relevance": "relevant",
  "access_status": "accessed",
  "accessed_at": "2026-08-21T14:30:00+08:00",
  "search_terms": ["recent travel documentary Staff Picks"],
  "sample_scope": "Eight current Staff Picks; four films watched beyond thumbnails",
  "discovery_mechanism": "Human-curated Staff Picks channel",
  "access_limitations": "Public video and metadata available; comments not sampled",
  "evidence_urls": ["https://vimeo.com/channels/staffpicks"],
  "roles": ["editorial", "author-discovery"],
  "keywords": ["observational", "human-scale", "motivated-cut"],
  "patterns": {
    "camera_movement": "Movement follows subject action instead of decorating static views",
    "emotional_peak": "Reaction and aftermath are held after the key action"
  }
}
```

For `restricted`, retain the same fields, state the exact limitation, and add `public_fallback_evidence_urls`. Limit claims to what those public pages, metadata, or thumbnails actually reveal.

A skipped record has this shape:

```json
{
  "source_id": "archdaily",
  "relevance": "skipped",
  "access_status": "not-accessed",
  "skip_reason": "The active family collection has no architecture or spatial-story emphasis"
}
```

## Live calibration summary

Provide these fields:

- `long_term_standards`: observations supported by professional, award, editor, or staff selections;
- `recent_platform_trends`: time-sensitive patterns from current platform samples;
- `author_style_signals`: patterns tied to named creators and not generalized;
- `cross_source_patterns`: each observation cites at least two `source_ids`;
- `applied_selection_rules`: executable rules for this collection;
- `pattern_dimensions`: concrete calibration for composition, light, color, viewpoint, subject distance, action/relationship, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame;
- `popularity_use`: a statement that popularity metrics were used only for discovery.

Each observation is an object with `observation` and `source_ids`.

## Authorized static mode

When connectivity is unavailable and the user explicitly agrees:

- set `calibration_mode` to `static-authorized` and `static_fallback_authorized` to `true`;
- add `static_authorization.authorized_at` and the user's actual confirmation in `user_confirmation`;
- keep sources required for the active material type marked `relevant`, set every source to `not-accessed`, and record the connectivity limitation;
- omit live-evidence fields such as access time, queries, samples, evidence URLs, keywords, and observed patterns;
- keep `recent_platform_trends`, `author_style_signals`, and `cross_source_patterns` empty;
- label any applied aesthetic guidance as static knowledge, not current evidence.

## Validate

```bash
python3 scripts/validate_reference_calibration.py \
  --input <reference-calibration.json>
```

- exit `0`, `ready-live`: current evidence and all source records are complete;
- exit `0`, `ready-static-authorized`: live evidence is unavailable and explicit authorization is recorded;
- exit `3`: screening must remain paused for user authorization;
- exit `2`: the evidence log is invalid or incomplete; fix it before culling.
