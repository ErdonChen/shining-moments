# Visual Reference Research

Reference research calibrates judgment before culling. It does not copy individual works, replace the user's taste, or turn popularity into a quality score. Only media actually visible or playable in the current run is evidence.

## Fixed opening order

Use [reference-source-map.json](reference-source-map.json) as the canonical registry and proceed in this order:

1. ask the topic: `mixed`, `landscape-travel`, `architecture-space`, `documentary-culture`, `portrait`, `family`, `friends`, `vlog-event`, or `custom`;
2. ask the media kinds: `photo`, `video`, or both;
3. run every applicable automatic source, then offer at most one optional manual enhancement;
4. after the reference gate is ready, ask `link` or `copy` delivery.

Do not ask users to select individual automatic sites. `mixed` and `custom` still use the same fixed pools, with search terms adapted to the brief. Account for every catalog source as attempted or not selected, with concrete limitations or a skip reason. X and Vimeo are not routed sources.

## Automatic calibration

Automatic sources require no user login or challenge.

### Photo pool

- [Wikimedia Commons Images](https://commons.wikimedia.org/wiki/Category:Images) (`wikimedia-commons`): location, architecture, history, culture, documentary context, and broadly licensed public media.
- [Flickr public content](https://www.flickr.com/explore) (`flickr-public`): real events, street scenes, community life, personal perspectives, and less-polished lived context.
- [Google Images](https://images.google.com/) (`google-images`): broad visual discovery across the web. It counts as one source, regardless of how many origin domains appear in results.

### Video pool

- [Wikimedia Commons Videos](https://commons.wikimedia.org/wiki/Category:Videos) (`wikimedia-commons`): documentary, historical, cultural, location, and public-media motion references.
- [Google Videos](https://www.google.com/videohp) (`google-videos`): broad discovery of motion, pacing, shot structure, and topic-specific video references. It counts as one source, regardless of origin domains.

A normal photo source counts only when a full image is visibly inspectable. Google Images also accepts an enlarged preview only when the origin URL is recorded; a thumbnail never counts. A video source counts only when actual playback is visibly inspectable. A reachable page, text, metadata, search snippet, blocked player, or remembered platform style never counts.

Record every failed automatic source with attempted URLs, timestamp, exact limitation, failure reason, `authentication_used: false`, and an empty visible-sample list. Do not silently replace one automatic source with an unrecorded site.

## Optional manual enhancement

Offer manual enhancement only after the automatic pass. Ask whether the user wants one extra source. If yes, ask for a human-verification source, a user-login source, or a custom URL. Recommend one source based on topic and media kind; the user may accept it, choose another listed source, or enter another URL.

### Human-verification enhancement

- [Unsplash](https://unsplash.com/) (`unsplash`): photos; useful for curated composition, light, landscape, travel, portrait, and lifestyle references.
- [Pexels](https://www.pexels.com/) (`pexels`): photos and videos; useful for people, lifestyle, general scenes, action, shot structure, and B-roll. One human-verification pass may be reused for both Pexels Photos and Pexels Videos in the same run. Never ask for a second Pexels verification merely because both media kinds were requested.

The user completes the challenge themselves in their own visible browser and confirms readiness. The Skill then inspects only visible full images or playing videos.

### User-login enhancement

- [Xiaohongshu](https://www.xiaohongshu.com/explore) (`xiaohongshu`): Chinese-language lifestyle, travel, local scenes, current short-form visual language, photos, and videos.
- [Instagram](https://www.instagram.com/) (`instagram`): contemporary portrait, lifestyle, creator, photo, and short-video expression.
- [YouTube](https://www.youtube.com/) (`youtube`): long- and short-form video narrative, shot organization, pacing, and editing structure.
- [Bilibili](https://www.bilibili.com/) (`bilibili`): Chinese-language Vlogs, events, culture, community video, and editing language.

The user chooses the source and logs in themselves in their own visible browser. The Skill never asks for or handles login material.

### Custom URL

Open a user-supplied URL first. If its media is publicly visible, inspect it directly. If a human-verification challenge appears, ask the user to complete it. Ask the user to log in only when the site actually requires login. Record the custom source as `manual-custom` and use the same full-image/video-playback evidence rules.

Never ask for, receive, store, or handle usernames, passwords, MFA codes, cookies, API keys, account credentials, or other authentication secrets. Never bypass a login wall, region restriction, paywall, CAPTCHA, or automation defense. Declining or failing manual enhancement does not cancel automatic calibration.

## Per-media readiness

Evaluate photos and videos separately. Each requested media kind is ready only when at least two distinct source IDs provide visible evidence in the current run. Successful automatic and manual sources may combine. Wikimedia Commons can count for both requested kinds when it supplies separate visible photo and video samples, but it remains one source within each gate.

- two or more sources: ready for that media kind;
- one source: partial;
- zero sources: unavailable.

When any requested kind is partial or unavailable, pause before inventory unless the user explicitly authorizes static aesthetic knowledge. Static guidance must be labeled as static, never as current visual observation.

## Evidence and synthesis

For every accessed source, record access time, search terms or discovery path, sample scope, exact visible sample URLs, media kind, visibility type, origin URL where required, concrete observations, access limitations, roles, keywords, and pattern dimensions. For failures, retain the attempted URLs and empty visible-sample list. For unselected manual sources, record why they were not selected.

Patterns may cover composition, light, color, viewpoint, subject distance, action and relationships, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame. A cross-source pattern must cite at least two actually visible sources. Keep long-term editorial standards, manual trend signals, and named-author signatures separate. Likes, ratings, views, follower counts, and ranking may help locate samples but never replace visual, narrative, technical, or relationship judgment.
