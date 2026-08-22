# Shining-Moments-Cut

English | [简体中文](README.md)

This repository is a collection of two Skills:

- **[Shining Moments](skills/shining-moments/README.en.md)**: an intelligent media-selection Skill that uses automatic references and optional enhanced references to screen photos and videos.
- **[Shining Cut](skills/shining-cut/README.en.md)**: an intelligent video-editing Skill that uses automatic references and optional enhanced references to create an editing script, storyboard, initial cut, and optional fine cut.

The recommended workflow is to select media with Shining Moments and then edit the selected videos with Shining Cut. Each Skill can also be used independently.

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

## Package layout

```text
skills/
├── shining-moments/
└── shining-cut/
```

Both directories are independent Skills. They can be installed together or separately.
