# Reference Calibration Evidence

Create `reference-calibration.json` after topic/media selection and before inventory or culling. Schema version 3 records fixed automatic attempts, at most one optional manual enhancement, per-media readiness, and only evidence visible in the current run.

## Readiness states

Evaluate every requested media kind independently. A photo or video gate needs two distinct visible sources; successful automatic and manual sources may combine.

| Per-media visible source count | Manual status | `calibration_mode` | Validator result |
|---:|---|---|---|
| 2 or more for every requested kind | declined / cannot-use | `automatic` | `ready-automatic` |
| 2 or more for every requested kind | completed with visible evidence | `manual-enhanced` | `ready-manual-enhanced` |
| any requested kind has exactly 1 | any | `partial` | exit `3`, `paused-partial` |
| any requested kind has 0 | any | `unavailable` when no gate has evidence, otherwise `partial` | exit `3` |
| partial/unavailable with explicit static approval | any | `static-authorized` | `ready-static-authorized-partial` or `ready-static-authorized-unavailable` |

Declining or failing the optional manual enhancement never blocks an otherwise ready automatic result. Manual evidence can complete a partial per-media gate, but only when its actual full image or video playback is recorded.

## Top-level structure

```json
{
  "schema_version": 3,
  "material_type": "vlog-event",
  "media_kinds": ["photo", "video"],
  "automatic_calibration": {
    "checked_at": "2026-08-22T14:00:00+08:00",
    "detail": "Photo and video automatic pools were attempted independently",
    "media": {
      "photo": {
        "status": "ready",
        "successful_source_ids": ["wikimedia-commons", "flickr-public", "google-images"],
        "failed_source_ids": [],
        "detail": "Three automatic photo sources exposed visible samples"
      },
      "video": {
        "status": "ready",
        "successful_source_ids": ["wikimedia-commons", "google-videos"],
        "failed_source_ids": [],
        "detail": "Two automatic video sources exposed playable samples"
      }
    }
  },
  "manual_enhancement": {
    "status": "declined",
    "mode": "none",
    "offered_source_ids": ["unsplash", "pexels", "xiaohongshu", "instagram", "youtube", "bilibili"],
    "selected_source_ids": [],
    "custom_sources": [],
    "user_readiness_confirmed": false,
    "detail": "The user declined one optional manual enhancement"
  },
  "calibration_mode": "automatic",
  "static_fallback_authorized": false,
  "sources": [],
  "calibration_summary": {}
}
```

`automatic_calibration.media` must contain exactly the requested `media_kinds`. Its successful and failed IDs must exactly match the applicable fixed automatic pool and the source evidence records. The automatic photo pool is `wikimedia-commons`, `flickr-public`, and `google-images`; the automatic video pool is `wikimedia-commons` and `google-videos`.

`manual_enhancement.mode` is `none`, `challenge`, `login`, or `custom`. A non-`none` mode selects exactly one source. Catalog modes offer every applicable manual source even though the workflow recommends only one; a custom URL adds exactly one `manual-custom` definition whose ID starts with `custom-`.

## Successful automatic source

```json
{
  "source_id": "google-images",
  "access_mode": "automatic",
  "selection_status": "selected",
  "access_status": "accessed",
  "calibration_use": "used",
  "authentication_used": false,
  "accessed_at": "2026-08-22T14:05:00+08:00",
  "search_terms": ["family travel meaningful interaction"],
  "sample_scope": "Four enlarged previews inspected",
  "discovery_mechanism": "Google Images search",
  "access_limitations": "Only enlarged previews with origin links counted",
  "visible_samples": [
    {
      "url": "https://images.google.com/example-preview",
      "origin_url": "https://example.org/original-photo-page",
      "media_kind": "photo",
      "visibility": "enlarged-preview",
      "observation": "A clear shared action establishes relationship and place"
    }
  ],
  "roles": ["editorial", "author-discovery"],
  "keywords": ["relationship", "sense-of-place"],
  "patterns": {
    "composition": "Shared action anchors the foreground against environmental context"
  }
}
```

Automatic records always set `authentication_used` to `false`. Normal photo samples require `full-image`; `google-images` permits `enlarged-preview` or `full-image` and always requires `origin_url`. Video samples require `video-playback`. Google Images and Google Videos each remain one source ID regardless of their result domains.

## Failed automatic source

```json
{
  "source_id": "google-videos",
  "access_mode": "automatic",
  "selection_status": "selected",
  "access_status": "failed",
  "calibration_use": "skipped",
  "authentication_used": false,
  "accessed_at": "2026-08-22T14:08:00+08:00",
  "search_terms": ["family travel video reference"],
  "attempted_urls": ["https://www.google.com/videohp"],
  "access_limitations": "Results appeared but no video playback was inspected",
  "failure_reason": "Search-result thumbnails do not satisfy video evidence",
  "visible_samples": []
}
```

Failures remain in the audit trail and contribute no evidence.

## Unselected manual source

```json
{
  "source_id": "instagram",
  "access_mode": "manual-login",
  "selection_status": "not-selected",
  "access_status": "not-accessed",
  "calibration_use": "skipped",
  "skip_reason": "The user chose no login enhancement"
}
```

Include exactly one record for every catalog entry, plus the selected custom definition when custom mode is used.

## Manual enhancement

### Human-verification source

Use `mode: "challenge"` with exactly one of `unsplash` or `pexels`. The user completes the challenge in their own visible browser. Pexels may contain both photo and video samples in one source record after one completed challenge. Do not ask for a second verification for Pexels Videos.

### User-login source

Use `mode: "login"` with exactly one of `xiaohongshu`, `instagram`, `youtube`, or `bilibili`. The user logs in themselves and confirms readiness.

### Custom URL

Use `mode: "custom"`, add one `manual-custom` source definition to `custom_sources`, append the corresponding source record, and record whether the URL was public, challenge-protected, or login-protected in `discovery_mechanism` and `access_limitations`.

An accessed manual source uses `user_visible_browser: true` and the same full-image/video-playback evidence fields as an automatic source. A selected source that exposes no visible media uses the failed-source shape. `cannot-use` must record that failed selected source; `completed` requires visible manual evidence.

Never include username, password, MFA, cookie, API-key, credential, token, or other authentication-secret fields anywhere in the payload.

## Calibration summary

For ready automatic or manual-enhanced states, provide:

- `long_term_standards`: non-empty observations citing successful automatic editorial sources;
- `recent_platform_trends`: optional observations citing successful manual trend sources only;
- `author_style_signals`: optional observations citing successful author-discovery sources;
- `cross_source_patterns`: at least one observation citing two or more successful visible sources;
- `applied_selection_rules`: executable rules for this collection;
- `pattern_dimensions`: concrete text for composition, light, color, viewpoint, subject distance, action/relationship, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame;
- `popularity_use`: state that popularity was discovery-only;
- `calibration_state_note`: name automatic or manual-enhanced state and limitations.

Each observation contains `observation` and `source_ids`. Never cite a failed, skipped, or unseen source.

## Partial, unavailable, and static-authorized

Without explicit static authorization, set `calibration_mode` to `partial` or `unavailable`, keep `static_fallback_authorized: false`, and stop when the validator exits `3`.

With explicit authorization, set `calibration_mode: "static-authorized"`, `static_fallback_authorized: true`, and add:

```json
{
  "static_authorization": {
    "authorized_at": "2026-08-22T14:20:00+08:00",
    "user_confirmation": "Continue with static standards despite the recorded live-reference limit"
  }
}
```

Retain partial evidence and limitations, keep `recent_platform_trends`, `author_style_signals`, and `cross_source_patterns` empty, and label all applied guidance as static.

## Validate

```bash
python3 scripts/validate_reference_calibration.py \
  --input <reference-calibration.json>
```

- exit `0`: a named ready state is printed;
- exit `3`: a per-media gate is partial/unavailable and static fallback is not authorized;
- exit `2`: the log is structurally invalid or overclaims visible evidence.
