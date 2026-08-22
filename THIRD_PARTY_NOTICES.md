# Third-Party Notices

This repository vendors two upstream Skills so a complete Shining Moments → Shining Cut workflow can be installed from one bundle. The upstream runtime scripts are copied without functional modification. For Codex validation, unsupported top-level frontmatter fields in Watch and the nested Manim Skill are moved under `metadata`; their verbatim upstream entrypoints remain beside them as `SKILL.upstream.md`. Video Use's top-level entrypoint has one trailing space removed and a bundle-aware setup note; its installer gains a bundle path that avoids cloning a duplicate checkout. Shining-Moments-Cut otherwise adds package-level orchestration, documentation, provenance, and validation around the snapshots.

## Watch / claude-video

- Project: [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
- Author: Bradley Bonanno (Brad Bonanno / `bradautomates`)
- Vendored snapshot: `83da59fa78c3eee9e20f515fe75c438bb5166efd`
- Vendored path: `skills/watch/`
- Adaptation: Codex-compatible frontmatter in `SKILL.md`; verbatim upstream entrypoint in `SKILL.upstream.md`
- License: MIT; the complete notice is preserved at `skills/watch/LICENSE`

## Video Use

- Project: [browser-use/video-use](https://github.com/browser-use/video-use)
- Author: Browser Use
- Vendored snapshot: `92c2b34e44c205cbc2acae7f6ca7c1c219d5dd66`
- Vendored path: `skills/video-use/`
- Adaptation: bundle-aware setup guidance, one trailing-space cleanup, and a no-duplicate-clone installer branch; the nested Manim Skill has Codex-compatible frontmatter and preserves its verbatim entrypoint as `skills/manim-video/SKILL.upstream.md`
- License: MIT; the complete notice is preserved at `skills/video-use/LICENSE`

The vendored snapshots remain subject to their respective upstream licenses. Shining-Moments-Cut's own license does not replace those notices.
