# Live Reference Research

Reference research is a required calibration step before culling. Observe current public evidence; do not substitute remembered platform style. Use references to calibrate visual language, not to copy individual works or replace the user's taste.

## Source accounting

Use [reference-source-map.json](reference-source-map.json) as the canonical registry. After the material type is known:

- visit every source whose `required_for` includes the active type;
- for `mixed`, visit all canonical sources;
- record every other canonical source as `skipped` with a specific project-relevance reason;
- for `custom`, select relevant sources from the registry and record why every other source is not relevant.

Do not reduce the required set because of time pressure. A site restriction is an access result to document, not permission to omit the source.

## What to observe

At each relevant source, search recent popular, featured, award-winning, editor-selected, staff-picked, latest, or otherwise representative public work. Record:

- access date and time;
- exact search terms, collection, channel, award page, or discovery path;
- sample scope, such as result count, galleries opened, videos watched, or thumbnails inspected;
- the visible mechanism: human editorial selection, awards, chronological feed, search ranking, popularity surface, or named-author page;
- access status and limitations, including login, region, paywall, JavaScript challenge, missing media, metadata-only access, or unavailable audio/video;
- evidence URLs, keywords, and concrete observed patterns;
- source role: `editorial`, `trend`, or `author-discovery`.

Patterns may cover composition, light, color, viewpoint, subject distance, action and relationships, camera movement, shot duration, pacing, transition, emotional peak, narrative function, opening frame, and cover frame. Record only what the inspected sample supports. Thumbnail-only access cannot support claims about full-video pacing or sound-image relationships.

## Canonical sources and useful public surfaces

### Travel, landscape, architecture, and documentary culture

- [500px](https://500px.com/) (`500px`) — current Popular, Editors' Choice, category search, and named photographers; observe still-image composition, light, weather, depth, and viewpoint.
- [YouTube](https://www.youtube.com/) (`youtube`) — recent search, curated channels, playlists, and named filmmakers; inspect actual videos when making movement, duration, pacing, transition, or emotional-payoff claims.
- [ShotDeck](https://shotdeck.com/) (`shotdeck`) — current searchable film stills and visible tags for framing, lighting, color, location, and emotion.
- [National Geographic Photography](https://www.nationalgeographic.com/photography/) (`national-geographic-photography`) — current photo-editor selections, galleries, and visual stories connecting place with human context.
- [ArchDaily](https://www.archdaily.com/) (`archdaily`) — current projects, search, and editorial features for spatial sequence, material, scale, circulation, and human use.
- [Dezeen](https://www.dezeen.com/) (`dezeen`) — current architecture/design projects, search, and editorial features for form, context, material, and contemporary presentation.

### Portrait, family, friendship, and relationships

- [Documentary Family Awards](https://documentaryfamilyawards.com/) (`documentary-family-awards`) — current awards, collections, and public stories for candid family dynamics and relationship beats.
- [Family Photojournalist Association](https://www.fpja.com/) (`family-photojournalist-association`) — current contest galleries and public features for unposed daily life, humor, care, and family rhythm.
- [LensCulture](https://www.lensculture.com/) (`lensculture`) — current awards, editorials, portrait and documentary series for sequencing, identity, and emotional ambiguity.
- [Magnum Photos](https://www.magnumphotos.com/) (`magnum-photos`) — current stories, essays, and photographer pages for decisive moments, context, and long-form human relationships.
- [This Is Reportage](https://thisisreportage.com/) (`this-is-reportage`) — current collections and story awards for anticipation, gesture, reaction, group dynamics, and unposed sequences.
- [Instagram](https://www.instagram.com/) (`instagram`) — current public posts, creator pages, hashtags, and Reels when accessible; use engagement only to discover samples.

### Video craft and emotional storytelling

- [Vimeo Staff Picks](https://vimeo.com/channels/staffpicks) (`vimeo-staff-picks`) — current human-curated films for shot duration, movement, transition, sound-image relationship, and emotional payoff.
- [NOWNESS](https://www.nowness.com/) (`nowness`) — current editorial films and series for authored visual language, performance, portrait, culture, and expressive pacing.
- [YouTube](https://www.youtube.com/) (`youtube`) — recent creator films and longer-form Vlogs; separate named-author grammar from platform-wide patterns.

### Current trends and author discovery

- [Xiaohongshu](https://www.xiaohongshu.com/explore) (`xiaohongshu`) — current public search/explore evidence for Chinese travel, portrait, family, lifestyle, vertical video, titles, and mobile storytelling.
- [X](https://x.com/) (`x`) — current search, public author accounts, threads, and linked work for discovering photographers, filmmakers, and distribution patterns.

## Access restrictions

If login, region, paywall, automation defense, or another restriction blocks a site:

1. record `restricted`, the attempted URL/search, timestamp, visible result, and exact limitation;
2. seek verifiable public evidence such as the site's public search page, official award/selection page, public creator page, official metadata/API, or a current indexed page;
3. label the evidence scope precisely, such as metadata-only or thumbnail-only;
4. do not claim observations the fallback evidence cannot support.

If no public evidence can be verified, the live calibration is incomplete. Report the gap instead of inventing a site style or pretending access succeeded.

## Calibration synthesis

Keep three evidence layers separate:

- **Long-term editorial standards:** repeated patterns from professional, award, editor, or staff selections.
- **Recent platform trends:** time-sensitive presentation and discovery patterns; never a quality score.
- **One-author signatures:** useful options, not universal rules.

Create a cross-source summary only from patterns repeated across at least two sources. Translate it into project-specific selection rules before inventory. Likes, ratings, views, follower counts, and ranking may locate samples but never replace visual, narrative, technical, or relationship judgment.

Write `reference-calibration.json` and validate it as described in [reference-calibration-schema.md](reference-calibration-schema.md) before culling.
