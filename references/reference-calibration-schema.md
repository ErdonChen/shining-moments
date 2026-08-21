# Reference Calibration Evidence

Create `reference-calibration.json` after source selection and before inventory or culling. The file records the current run's actual visible evidence, source failures, optional manual enhancement, and readiness state. It is not a cache of permanent site style.

## Readiness states

| Automatic visible sources | Manual status | `calibration_mode` | Validator result |
|---:|---|---|---|
| 2 or more | declined / cannot-use | `automatic` | `ready-automatic` |
| 2 or more | completed with visible evidence | `manual-enhanced` | `ready-manual-enhanced` |
| 1 | any | `partial` | exit `3`, pause for static-fallback decision |
| 0 | any | `unavailable` | exit `3`, pause for static-fallback decision |
| 0 or 1 | any, explicit static approval | `static-authorized` | `ready-static-authorized-partial` or `ready-static-authorized-unavailable` |

Manual evidence never satisfies the two-source automatic gate. Declining or being unable to use manual enhancement does not block an otherwise ready automatic workflow.

## Top-level structure

```json
{
  "schema_version": 2,
  "material_type": "vlog-event",
  "media_kinds": ["photo", "video"],
  "automatic_selection": {
    "offered_source_ids": ["unsplash", "pexels-photos", "flickr-public", "wikimedia-commons-photos", "pexels-videos", "pixabay-videos", "mixkit", "wikimedia-commons-videos"],
    "default_source_ids": ["unsplash", "pexels-photos", "flickr-public", "pexels-videos", "pixabay-videos", "mixkit", "wikimedia-commons-videos"],
    "selected_source_ids": ["unsplash", "pexels-photos", "flickr-public", "pexels-videos", "pixabay-videos", "mixkit", "wikimedia-commons-videos"],
    "selection_basis": "type-default"
  },
  "automatic_calibration": {
    "status": "ready",
    "checked_at": "2026-08-21T14:25:00+08:00",
    "successful_source_ids": ["unsplash", "pexels-videos"],
    "failed_source_ids": ["pexels-photos", "flickr-public", "pixabay-videos", "mixkit", "wikimedia-commons-videos"],
    "detail": "Two automatic sources returned actual visible media; other selected sources failed and were skipped"
  },
  "manual_enhancement": {
    "status": "declined",
    "offered_source_ids": ["youtube", "bilibili", "vimeo", "instagram", "xiaohongshu"],
    "selected_source_ids": [],
    "user_readiness_confirmed": false,
    "detail": "The user declined optional manual enhancement; automatic research continued"
  },
  "calibration_mode": "automatic",
  "static_fallback_authorized": false,
  "sources": [],
  "calibration_summary": {}
}
```

`offered_source_ids` must contain every applicable catalog source. `default_source_ids` comes from the material type and media kinds. When the user does not choose sources, set `selection_basis` to `type-default` and copy the defaults into `selected_source_ids`. Use `user-selected` for an explicit subset and `custom-brief` only for custom material.

## Successful automatic source

```json
{
  "source_id": "unsplash",
  "access_mode": "automatic",
  "selection_status": "selected",
  "access_status": "accessed",
  "calibration_use": "used",
  "authentication_used": false,
  "accessed_at": "2026-08-21T14:30:00+08:00",
  "search_terms": ["Japan travel dawn lake"],
  "sample_scope": "Four full images opened and visibly inspected",
  "discovery_mechanism": "Public search results",
  "access_limitations": "No material limitation in the inspected sample",
  "visible_samples": [
    {
      "url": "https://unsplash.com/photos/example",
      "media_kind": "photo",
      "visibility": "full-image",
      "observation": "The foreground figure establishes scale against layered dawn haze"
    }
  ],
  "roles": ["editorial", "author-discovery"],
  "keywords": ["human-scale", "layered-depth"],
  "patterns": {
    "composition": "A small foreground subject anchors a deep landscape"
  }
}
```

Automatic sources always set `authentication_used` to `false`. A photo sample requires `full-image`; a video sample requires `video-playback`. Home pages, text, metadata, search snippets, thumbnails, unavailable players, and remembered styles are not visible samples.

## Failed selected source

```json
{
  "source_id": "mixkit",
  "access_mode": "automatic",
  "selection_status": "selected",
  "access_status": "failed",
  "calibration_use": "skipped",
  "authentication_used": false,
  "accessed_at": "2026-08-21T14:32:00+08:00",
  "search_terms": ["family reunion"],
  "attempted_urls": ["https://mixkit.co/free-stock-video/"],
  "access_limitations": "The page loaded but no video playback was visible",
  "failure_reason": "Page-only access cannot support visual calibration",
  "visible_samples": []
}
```

Failures remain in the audit trail and are skipped from calibration. Do not replace them with text-only, page-only, indexed, or remembered evidence.

## Unselected source

```json
{
  "source_id": "wikimedia-commons-photos",
  "access_mode": "automatic",
  "selection_status": "not-selected",
  "access_status": "not-accessed",
  "calibration_use": "skipped",
  "skip_reason": "Not part of the user's selected automatic subset"
}
```

Include exactly one source record for every catalog entry, including manual sources that were not offered or selected.

## Manual enhancement

Manual enhancement can use applicable YouTube, Bilibili, Vimeo, Instagram, and Xiaohongshu sources. Before collection, the user completes login or challenges themselves in their own visible browser and confirms readiness plus selected sources. The Skill never asks for, receives, stores, or handles account credentials or any other authentication secrets and never bypasses protection.

An accessed manual source uses the same evidence fields as an accessed automatic source, replaces `authentication_used` with `user_visible_browser: true`, and must include actual `full-image` or `video-playback` samples. A selected manual source that cannot expose visible media uses the failed-source shape and contributes no trend or author claim.

Use `manual_enhancement.status` as follows:

- `declined`: no selected sources, readiness is false, and automatic work continues;
- `cannot-use`: selected or attempted sources produced no usable visible manual evidence;
- `completed`: readiness is true, at least one selected manual source supplied visible evidence, and `calibration_mode` is `manual-enhanced` when automatic calibration is ready.

## Calibration summary

For ready automatic or manual-enhanced states, provide:

- `long_term_standards`: observations citing successful automatic editorial sources;
- `recent_platform_trends`: optional observations citing successful manual trend sources only;
- `author_style_signals`: optional observations tied to successful sources with an author-discovery role;
- `cross_source_patterns`: at least one observation citing two or more successful automatic sources;
- `applied_selection_rules`: executable rules for the collection;
- `pattern_dimensions`: concrete text for composition, light, color, viewpoint, subject distance, action/relationship, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame;
- `popularity_use`: state that popularity was discovery-only;
- `calibration_state_note`: state whether the result is automatic or manual-enhanced and summarize failures/limitations.

Each observation has `observation` and `source_ids`. A summary may cite only source records with actual visible samples.

## Partial, unavailable, and static-authorized states

Set `automatic_calibration.status` from the successful automatic source count: `partial` for one and `unavailable` for zero. Without explicit static authorization, use the same value for `calibration_mode`, set `static_fallback_authorized` to `false`, and stop when the validator exits `3`.

If the user explicitly authorizes static fallback:

- set `calibration_mode` to `static-authorized` and `static_fallback_authorized` to `true`;
- add `static_authorization.authorized_at` and `user_confirmation`;
- retain all partial evidence and failed-source limitations;
- keep `recent_platform_trends`, `author_style_signals`, and `cross_source_patterns` empty;
- label applied guidance and `calibration_state_note` as static, not current visual calibration.

## Validate

```bash
python3 scripts/validate_reference_calibration.py \
  --input <reference-calibration.json>
```

- exit `0`: a named ready state is printed;
- exit `3`: automatic calibration is partial/unavailable and the user has not authorized static fallback;
- exit `2`: the evidence log is structurally invalid or overclaims what was visible.
