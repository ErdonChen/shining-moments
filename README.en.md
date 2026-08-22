# Shining-Moments-Cut

English | [简体中文](README.md)

This repository is a complete media-selection and editing bundle containing four independently installable Skills:

- **[Shining Moments](skills/shining-moments/README.en.md)**: an intelligent media-selection Skill that uses automatic references and optional enhanced references to screen photos and videos.
- **[Shining Cut](skills/shining-cut/README.en.md)**: an intelligent video-editing Skill that uses automatic references and optional enhanced references to create an editing script, storyboard, initial cut, and optional fine cut.
- **[Watch](skills/watch/SKILL.md)**: the video-understanding Skill from `bradautomates/claude-video`, used to decode video, extract timestamped frames, and obtain caption/transcript evidence.
- **[Video Use](skills/video-use/README.md)**: the conversational editing Skill from `browser-use/video-use`, used for word-level transcription, EDLs, rendering, subtitles, animations, and output self-evaluation.

The recommended workflow is to select media with Shining Moments, then let Shining Cut orchestrate Watch and Video Use for reference calibration, editing, and QA. Each Skill can also be used independently.

## Shining Moments: find the moments worth keeping

Shining Moments uses reference calibration to screen photos and videos, retains uncertain media that may still carry meaningful memories, and leaves the final choice to the user.

- **Automatic references**: photos use Wikimedia Commons Images, Flickr, and Google Images; videos use Wikimedia Commons Videos and Google Videos.
- **Enhanced references (optional)**: depending on the media type, the user may choose Unsplash, Pexels, Xiaohongshu, Instagram, YouTube, Bilibili, or a custom URL. Any challenge or login is completed by the user.
- **Outline**: confirm the topic and references → create primary, backup, and memory selections → deliver manifests and original-media mappings.

After selection, Shining Cut can continue by intelligently editing the selected videos.

## Shining Cut: turn selected videos into a story

Shining Cut extracts pacing, structure, shot language, sound, and color direction from relevant reference videos, then maps those patterns onto the user's own footage.

- **Automatic references**: Google Videos and Wikimedia Commons Videos.
- **Enhanced references (optional)**: YouTube or Bilibili; the user may also submit a reference-video URL.
- **Outline**: confirm the topic and reference target → create the script, storyboard, and initial cut with a primary grade → optionally create a fine cut and secondary grade.

If the user did not use Shining Moments, Shining Cut first checks whether the footage was screened elsewhere. Already-screened footage can be supplied directly; unscreened footage prompts a recommendation to use Shining Moments first.

## Integration model

- Shining Moments uses Watch for decoded frames and timestamped evidence during video screening, but never starts an edit automatically.
- Shining Cut owns source mapping, reference calibration, the script/storyboard, and its three centralized confirmations. An approved Shining Cut blueprint satisfies Video Use's strategy-confirmation gate, avoiding a duplicate approval round.
- Watch is responsible for seeing and hearing; Video Use is responsible for editing and verification. Shining Cut retains end-to-end orchestration, original-media mappings, and delivery records.
- Both upstream Skills are vendored as pinned snapshots with their runtime files, licenses, and provenance intact. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [UPSTREAM_SOURCES.json](UPSTREAM_SOURCES.json).

## Package layout

```text
skills/
├── shining-moments/
├── shining-cut/
├── watch/
└── video-use/
    ├── helpers/
    └── skills/manim-video/
```

Install the complete directory for each Skill, not only its `SKILL.md`: Watch requires its sibling `scripts/`, while Video Use requires its sibling `helpers/`, `pyproject.toml`, and vendored `skills/manim-video/`.

## Environment requirements and acknowledgements

### Watch (from `bradautomates/claude-video`)

- Python 3, plus `ffmpeg`, `ffprobe`, and `yt-dlp` available on `PATH`.
- The agent host must allow local command execution and image reading for the extracted JPEG frames. Use `python` on Windows and typically `python3` on macOS/Linux.
- No transcription key is required when public native captions are available. For videos without captions, a Groq or OpenAI API key can enable the optional Whisper fallback. Only extracted audio is sent to the selected service when that fallback is used; the video itself is not uploaded.

### Video Use (from `browser-use/video-use`)

- Python `>=3.10`; run `uv sync` or `pip install -e .` inside `skills/video-use/` to install `requests`, `librosa`, `matplotlib`, `pillow`, and `numpy`.
- `ffmpeg` and `ffprobe` are hard requirements. `yt-dlp` is needed only for downloading online sources.
- An ElevenLabs API key is required for Scribe word-level transcription. Configure it through the environment or an uncommitted `.env`; never commit it to this repository.
- Node.js/npm are needed only for HyperFrames or Remotion animation slots; HyperFrames currently requires Node.js 22+. Install Manim and other animation engines lazily when a project uses them.

### Thanks

- Thanks to **Bradley Bonanno (Brad Bonanno / [bradautomates](https://github.com/bradautomates))** for creating [claude-video](https://github.com/bradautomates/claude-video) and the Watch Skill. This bundle preserves its MIT license and copyright notice.
- Thanks to the **[Browser Use](https://github.com/browser-use)** team for creating [video-use](https://github.com/browser-use/video-use). This bundle preserves its MIT license and copyright notice.
