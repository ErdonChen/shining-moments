# Shining Moments Reference And Selection Flow Design

## Goal

Make live visual calibration usable under real anti-bot and login constraints, while keeping meaningful, high-quality, technically usable media as the primary selection objective. Percentage limits prevent indiscriminate selection; they do not force good, distinct material out of the shortlist.

## Opening flow

1. Ask for the material topic: `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`.
2. Ask for media kinds: `photo`, `video`, or both.
3. Run every applicable automatic source without a source checklist:
   - photo: Wikimedia Commons Images, Flickr Public Content, Google Images;
   - video: Wikimedia Commons Videos, Google Videos.
4. Offer one optional manual enhancement:
   - challenge-assisted: recommend one of Unsplash, Pexels Photos, or Pexels Videos from the topic and media kinds. For mixed photo/video, prefer Pexels and reuse the same verified browser session for both Pexels surfaces;
   - login-assisted: recommend one of Xiaohongshu, Instagram, YouTube, or Bilibili from the topic, language, audience, and media kinds;
   - custom URL: open it first, use public content directly, ask the user to complete a challenge when shown, and ask the user to log in only when the site requires it.
5. The user completes every challenge or login in their visible browser. The Skill never requests, receives, stores, or processes usernames, passwords, MFA codes, cookies, API keys, or other authentication secrets, and never bypasses protection.
6. Ask only `link` or `copy`. Link mode uses source links and video timecodes. Copy mode creates reviewable photo derivatives and lightweight video clips without copying full high-bitrate source videos.

## Reference evidence

- Calibrate photo and video independently. Each requested media kind needs two independent visible sources.
- Automatic and manual evidence may combine to satisfy a media-kind gate. Record this as hybrid/manual-enhanced readiness.
- Google Images and Google Videos each count as one catalog source for their own media kind. They do not expand into multiple sources because results come from multiple domains.
- A Google Images sample must be an enlarged preview that supports composition, light, and subject judgment and must retain the origin URL. Thumbnails do not count.
- A video sample counts only when playback is visible.
- If a requested media kind has fewer than two visible sources, record partial/unavailable honestly and require explicit static-fallback authorization before screening.

## Selection guardrails

Quality, meaning, technical usability, distinct story function, and relationship value outrank percentages. The 10%/25% values trigger a second review; they are not quotas or hard caps.

### Photos

- Denominator: all deduplicated unique photo candidates. RAW+JPEG pairs and byte-identical files count once.
- Trigger: select candidates over 10% or review candidates over 25%.
- Second review: remove redundancy and weak alternatives first. Weaker select candidates move to review; weaker review candidates move to `not_selected`.
- Keep non-redundant high-quality, meaningful, irreplaceable, or distinct-story candidates even when the final ratio remains over the trigger. Every retained overflow candidate needs concrete selection evidence.
- Small collections retain at least one qualified select and one genuinely useful review candidate when present.

### Videos

- Denominator: total duration of deduplicated readable source videos. Byte-identical videos count once; unreadable-duration sources are reported outside the denominator.
- Numerators: the union of non-overlapping select intervals and the union of non-overlapping review intervals. An interval assigned to multiple decisions counts only at the highest priority.
- Trigger: select duration over 10% or review duration over 25%.
- Second review: tighten dead air around complete actions, dialogue, and emotional beats, then demote weaker whole intervals from select to review and review to `not_selected`.
- A collection with at most 60 seconds of total readable video duration skips percentage compression and keeps its natural first-pass decisions.
- A longer collection may keep at least one complete meaningful action, dialogue, or emotional interval even when it exceeds the trigger.
- Final ratios may stay above 10%/25% when remaining intervals are non-redundant and have concrete quality, meaning, relationship, or narrative evidence.

## Reporting and safety

- Preserve `select`, `review`, `memory`, `not_selected`, and `excluded`; never use `memory` as overflow storage.
- Report initial and final photo counts/ratios, video durations/ratios, trigger decisions, demotions, interval trims, and every evidence-backed retained overflow exception.
- Keep source media read-only. Never move, overwrite, delete, or recommend deleting originals.

## Delivery scope

Update the source repository, test it, synchronize the installed local Skill, validate source/install parity, and create a local commit. Do not push to GitHub, modify PRs, or change repository visibility.
