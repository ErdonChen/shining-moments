# Baseline Findings

Failures observed before the Skill existed:

- A general video-curation response proposed exporting useful intervals, stabilized previews, and a review reel during the first pass, creating avoidable storage use.
- It proposed a later deletion-approval list even though the intended workflow never deletes or moves originals.
- It treated an emotionally unique shaky family clip mainly as a stabilization task instead of preserving it for user re-screening whenever people and interaction remained recognizable.
- General responses varied between copies, reports, contact sheets, quarantine folders, and links instead of asking for link versus copy and defaulting to links.
- An earlier conservative rule sent every usable duplicate to the review folder. On large burst-heavy collections this could leave more than half the deduplicated candidates in `review`, which was effectively no filtering. The corrected workflow leaves naturally small review sets unchanged, but only when review exceeds its conditional ceiling does a second redundancy-first pass move usable non-shortlisted frames to `not_selected`.
