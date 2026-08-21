# Visual Reference Research

Reference research calibrates visual judgment before culling. It does not copy individual works, replace the user's taste, or turn popularity into a quality score. Use only evidence actually visible in the current run.

## Route before research

Use [reference-source-map.json](reference-source-map.json) as the canonical registry:

1. choose the material type and record whether the scope contains photos, videos, or both;
2. show every applicable automatic public source and the type-specific default selection;
3. accept a user-selected automatic subset, or use the defaults when the user does not select;
4. then offer the applicable manual-enhancement sources;
5. account for every catalog source as selected or not selected, with a concrete reason.

For `mixed`, route the automatic photo and video pools that match the stated media kinds. For `custom`, route from the user's brief. A URL or image supplied by the user is an input reference, not a catalog source and not evidence that a routed source was reached. X is neither an automatic nor a manual-enhancement source.

## Automatic public sources

Automatic sources must require no login and must return actual visible media in this run.

### Photo pool

- [Unsplash](https://unsplash.com/) (`unsplash`)
- [Pexels Photos](https://www.pexels.com/) (`pexels-photos`)
- [Flickr public content](https://www.flickr.com/explore) (`flickr-public`)
- [Wikimedia Commons images](https://commons.wikimedia.org/wiki/Main_Page) (`wikimedia-commons-photos`)

### Video pool

- [Pexels Videos](https://www.pexels.com/videos/) (`pexels-videos`)
- [Pixabay Videos](https://pixabay.com/videos/) (`pixabay-videos`)
- [Mixkit](https://mixkit.co/free-stock-video/) (`mixkit`)
- [Wikimedia Commons videos](https://commons.wikimedia.org/wiki/Category:Videos) (`wikimedia-commons-videos`) when suitable for the active type

A photo source counts only when a full image is visibly inspectable. A video source counts only when actual video playback is visibly inspectable. A reachable home page, text, metadata, search snippet, thumbnail, blocked player, or remembered platform style does not count. Record a failed selected source as skipped from calibration, with its attempted URLs, timestamp, exact limitation, failure reason, and an empty visible-sample list.

Automatic visual calibration is `ready` only when at least two suitable automatic sources provide visible samples. One source is `partial`; zero is `unavailable`. Evidence from the manual layer may enhance a ready result but never replaces this two-source automatic gate.

## Optional manual enhancement

Offer only the sources applicable to the selected type and media kinds:

- [YouTube](https://www.youtube.com/) (`youtube`)
- [Bilibili](https://www.bilibili.com/) (`bilibili`)
- [Vimeo](https://vimeo.com/) (`vimeo`)
- [Instagram](https://www.instagram.com/) (`instagram`)
- [Xiaohongshu](https://www.xiaohongshu.com/explore) (`xiaohongshu`)

If the user selects manual enhancement, instruct them to finish login or any challenge themselves in their own visible browser, then confirm readiness and the selected sources. Never request, receive, store, or handle a username, password, MFA code, cookie, account credential, or other authentication secret. Never bypass a login wall, region restriction, paywall, CAPTCHA, or automation defense. Observe only content actually visible in the user's browser.

Declining or being unable to use manual enhancement continues with automatic public sources. Record the manual status as `declined`, `cannot-use`, or `completed`; failed selected sources retain honest limitations and contribute no trend or style claims.

## What to record

For each accessed source, record:

- access date and time;
- exact search terms, collection, channel, or discovery path;
- sample scope and visible discovery mechanism;
- actual visible sample URLs, media kind, visibility type, and a concrete observation;
- access limitations;
- source role, keywords, and observed pattern dimensions.

For each failure, record the attempted URLs, search terms, access time, limitation, and failure reason. For each unselected source, record why it was not selected. Do not convert failure pages, public metadata, or indexed text into visual evidence.

Patterns may cover composition, light, color, viewpoint, subject distance, action and relationships, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame. Record only what the inspected samples support.

## Calibration synthesis

Keep these evidence layers separate:

- **Automatic cross-source patterns:** repeated visual evidence supported by at least two successful automatic sources.
- **Long-term standards:** patterns supported by automatic editorial or curated samples.
- **Manual trend signals:** optional, time-sensitive evidence from actually visible manual sources.
- **One-author signatures:** optional choices tied to named creators, not universal rules.

Likes, ratings, views, follower counts, and ranking may help locate manual samples but never replace visual, narrative, technical, or relationship judgment. Write `reference-calibration.json` and validate it with [reference-calibration-schema.md](reference-calibration-schema.md) before inventory or culling.
