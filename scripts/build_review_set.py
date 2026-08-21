#!/usr/bin/env python3
"""Build a non-destructive review set from a reviewed CSV manifest."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


CATEGORY_DIRS = {
    "select": "01_主选",
    "review": "02_备选_用户复筛",
    "memory": "03_纪念留档",
}

CATEGORY_PRIORITY = {
    "select": 0,
    "review": 1,
    "memory": 2,
}

DECISION_ALIASES = {
    "select": "select",
    "主选": "select",
    "必选": "select",
    "review": "review",
    "备选": "review",
    "复筛": "review",
    "memory": "memory",
    "留档": "memory",
    "纪念留档": "memory",
    "excluded": "excluded",
    "exclude": "excluded",
    "排除": "excluded",
    "淘汰": "excluded",
}

REQUIRED_COLUMNS = {"source_path", "decision", "reason"}
VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mts",
    ".webm",
}
RAW_EXTENSIONS = {
    ".3fr",
    ".arw",
    ".cr2",
    ".cr3",
    ".dng",
    ".erf",
    ".fff",
    ".iiq",
    ".kdc",
    ".mef",
    ".mos",
    ".mrw",
    ".nef",
    ".nrw",
    ".orf",
    ".pef",
    ".raf",
    ".raw",
    ".rw2",
    ".rwl",
    ".sr2",
    ".srf",
    ".srw",
    ".x3f",
}
JPEG_EXTENSIONS = {".jpg", ".jpeg"}
OUTPUT_FIELDS = [
    "source_path",
    "decision",
    "reason",
    "start_time",
    "end_time",
    "paired_jpeg_path",
    "organized_path",
    "review_source_path",
    "review_asset_kind",
    "generation_status",
    "generation_detail",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create links or copies for a conservative first-pass media review."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=("link", "copy"), default="link")
    parser.add_argument(
        "--video-delivery",
        choices=("auto", "timecodes", "clips"),
        default="auto",
        help=(
            "auto exports candidate clips in copy mode and keeps timecodes in link "
            "mode; explicit timecodes or clips override that default."
        ),
    )
    parser.add_argument(
        "--ffmpeg",
        default="ffmpeg",
        help="ffmpeg executable used only when --video-delivery clips is selected.",
    )
    parser.add_argument(
        "--ffprobe",
        default="ffprobe",
        help="ffprobe executable used to validate clip timecodes.",
    )
    parser.add_argument(
        "--raw-converter",
        default="auto",
        help=(
            "RAW converter executable. 'auto' checks magick, rawtherapee-cli, "
            "darktable-cli, then sips; other executables must accept SOURCE DESTINATION."
        ),
    )
    return parser.parse_args()


def normalize_decision(value: str, row_number: int) -> str:
    normalized = DECISION_ALIASES.get(value.strip().lower())
    if normalized is None:
        allowed = ", ".join(sorted(CATEGORY_DIRS | {"excluded"}))
        raise ValueError(
            f"row {row_number}: unsupported decision {value!r}; use one of {allowed}"
        )
    return normalized


def find_same_stem_jpeg(source: Path) -> Path | None:
    candidates = [
        path
        for path in source.parent.iterdir()
        if path.is_file()
        and path.resolve() != source.resolve()
        and path.stem.casefold() == source.stem.casefold()
        and path.suffix.lower() in JPEG_EXTENSIONS
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda path: (
            0 if path.suffix.lower() == ".jpg" else 1,
            path.name.casefold(),
        ),
    )[0].resolve()


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"manifest does not exist: {path}")

    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                "manifest is missing required columns: " + ", ".join(sorted(missing))
            )

        for row_number, raw in enumerate(reader, start=2):
            source_value = (raw.get("source_path") or "").strip()
            if not source_value:
                raise ValueError(f"row {row_number}: source_path is empty")

            source = Path(source_value).expanduser().resolve()
            if not source.is_file():
                raise ValueError(f"row {row_number}: source is not a file: {source}")

            decision = normalize_decision(raw.get("decision") or "", row_number)
            reason = (raw.get("reason") or "").strip()
            if not reason:
                raise ValueError(f"row {row_number}: reason is empty")
            start_time = (raw.get("start_time") or "").strip()
            end_time = (raw.get("end_time") or "").strip()
            if bool(start_time) != bool(end_time):
                raise ValueError(
                    f"row {row_number}: start_time and end_time must be provided together"
                )
            paired_jpeg_value = (raw.get("paired_jpeg_path") or "").strip()
            paired_jpeg_path = ""
            if paired_jpeg_value:
                paired_jpeg = Path(paired_jpeg_value).expanduser().resolve()
                if not paired_jpeg.is_file():
                    raise ValueError(
                        f"row {row_number}: paired JPEG is not a file: {paired_jpeg}"
                    )
                paired_jpeg_path = str(paired_jpeg)
            elif source.suffix.lower() in RAW_EXTENSIONS:
                paired_jpeg = find_same_stem_jpeg(source)
                if paired_jpeg is not None:
                    paired_jpeg_path = str(paired_jpeg)
            rows.append(
                {
                    "source_path": str(source),
                    "decision": decision,
                    "reason": reason,
                    "start_time": start_time,
                    "end_time": end_time,
                    "paired_jpeg_path": paired_jpeg_path,
                    "organized_path": "",
                    "review_source_path": "",
                    "review_asset_kind": "",
                    "generation_status": "",
                    "generation_detail": "",
                }
            )

    if not rows:
        raise ValueError("manifest contains no media rows")
    return rows


def unique_destination(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    if not candidate.exists() and not candidate.is_symlink():
        return candidate

    source_name = Path(filename)
    stem = source_name.stem
    suffix = source_name.suffix
    counter = 2
    while True:
        candidate = folder / f"{stem}__{counter}{suffix}"
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
        counter += 1


def place_media(source: Path, destination: Path, mode: str) -> None:
    if mode == "link":
        os.symlink(source, destination)
    else:
        shutil.copy2(source, destination)


def is_video(path: str) -> bool:
    return Path(path).suffix.lower() in VIDEO_EXTENSIONS


def is_raw_photo(path: str) -> bool:
    return Path(path).suffix.lower() in RAW_EXTENSIONS


def resolve_video_delivery(mode: str, video_delivery: str) -> str:
    if video_delivery != "auto":
        return video_delivery
    return "clips" if mode == "copy" else "timecodes"


def should_export_clip(row: dict[str, str], video_delivery: str) -> bool:
    return (
        video_delivery == "clips"
        and row["decision"] != "excluded"
        and is_video(row["source_path"])
        and bool(row["start_time"])
        and bool(row["end_time"])
    )


def parse_timecode(value: str) -> float:
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise ValueError(f"invalid timecode {value!r}; use MM:SS or HH:MM:SS")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise ValueError(f"invalid timecode {value!r}") from exc
    if any(number < 0 for number in numbers):
        raise ValueError(f"invalid negative timecode {value!r}")
    if numbers[-1] >= 60 or (len(numbers) == 3 and numbers[-2] >= 60):
        raise ValueError(f"invalid timecode component in {value!r}")
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]


def clip_filename(source: Path, start_time: str, end_time: str) -> str:
    def safe(value: str) -> str:
        return re.sub(r"[^0-9A-Za-z]+", "-", value).strip("-")

    return f"{source.stem}__{safe(start_time)}_to_{safe(end_time)}.mp4"


def resolve_executable(executable: str, label: str) -> str:
    if os.sep in executable:
        candidate = Path(executable).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise ValueError(f"{label} executable is unavailable: {candidate}")
        return str(candidate)
    resolved = shutil.which(executable)
    if resolved is None:
        raise ValueError(f"{label} executable is unavailable: {executable}")
    return resolved


def resolve_raw_converter(executable: str) -> str | None:
    if executable != "auto":
        try:
            return resolve_executable(executable, "RAW converter")
        except ValueError:
            # Missing RAW support is a per-asset partial failure, not a reason
            # to suppress the rest of the review set and its audit trail.
            return None
    for candidate in ("magick", "rawtherapee-cli", "darktable-cli", "sips"):
        resolved = shutil.which(candidate)
        if resolved is not None:
            return resolved
    return None


def raw_converter_command(
    converter: str,
    source: Path,
    destination: Path,
) -> list[str]:
    name = Path(converter).name.lower()
    if name in {"magick", "convert"}:
        return [
            converter,
            str(source),
            "-auto-orient",
            "-colorspace",
            "sRGB",
            "-quality",
            "85",
            str(destination),
        ]
    if name == "rawtherapee-cli":
        return [converter, "-o", str(destination), "-j85", "-c", str(source)]
    if name == "darktable-cli":
        return [
            converter,
            str(source),
            str(destination),
            "--core",
            "--conf",
            "plugins/imageio/format/jpeg/quality=85",
        ]
    if name == "sips":
        return [
            converter,
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            "85",
            "--out",
            str(destination),
            str(source),
        ]
    return [converter, str(source), str(destination)]


def convert_raw_to_jpeg(
    source: Path,
    destination: Path,
    converter: str,
) -> None:
    result = subprocess.run(
        raw_converter_command(converter, source, destination),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        detail = result.stderr.strip() or result.stdout.strip() or "no JPEG was created"
        raise OSError(f"failed to convert RAW {source.name}: {detail[-500:]}")


def probe_duration(source: Path, ffprobe: str) -> float:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(source),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        detail = result.stderr.strip() or "duration was unavailable"
        raise OSError(f"failed to inspect {source.name}: {detail[-500:]}") from exc
    if result.returncode != 0 or duration <= 0:
        detail = result.stderr.strip() or "invalid duration"
        raise OSError(f"failed to inspect {source.name}: {detail[-500:]}")
    return duration


def validate_clip_rows(rows: list[dict[str, str]], ffprobe: str) -> None:
    durations: dict[str, float] = {}
    for row in rows:
        if row["decision"] == "excluded":
            continue
        if not is_video(row["source_path"]):
            continue
        if not row["start_time"] or not row["end_time"]:
            raise ValueError(
                "clip delivery requires start_time and end_time for every "
                f"selected or review video row: {row['source_path']}"
            )
        start_seconds = parse_timecode(row["start_time"])
        end_seconds = parse_timecode(row["end_time"])
        if end_seconds <= start_seconds:
            raise ValueError(
                f"clip end must be after start: {row['start_time']} - {row['end_time']}"
            )
        source_path = row["source_path"]
        duration = durations.get(source_path)
        if duration is None:
            duration = probe_duration(Path(source_path), ffprobe)
            durations[source_path] = duration
        if end_seconds > duration + 0.05:
            raise ValueError(
                f"clip end {row['end_time']} exceeds {Path(source_path).name} "
                f"duration {duration:.3f}s"
            )


def estimate_review_storage(
    rows: list[dict[str, str]],
    mode: str,
    video_delivery: str,
) -> int:
    """Return a conservative preflight estimate for review-set bytes.

    The fixed allowance covers manifests, the report, directories, and links.
    Generated RAW JPEG sizes cannot be known in advance, so the estimate uses
    roughly one-third of the RAW size (bounded by the RAW itself). Video uses
    the configured 3 Mbps video ceiling plus 128 kbps audio and 10% overhead.
    """
    estimate = 64 * 1024
    clip_keys: set[tuple[str, str, str, str]] = set()
    for row in rows:
        if not should_export_clip(row, video_delivery):
            continue
        key = (
            row["source_path"],
            row["decision"],
            row["start_time"],
            row["end_time"],
        )
        if key in clip_keys:
            continue
        clip_keys.add(key)
        duration = parse_timecode(row["end_time"]) - parse_timecode(row["start_time"])
        estimate += max(1, int(duration * (3_000_000 + 128_000) / 8 * 1.10))

    if mode != "copy":
        return estimate

    photo_rows: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["decision"] == "excluded" or is_video(row["source_path"]):
            continue
        current = photo_rows.get(row["source_path"])
        if current is None or CATEGORY_PRIORITY[row["decision"]] < CATEGORY_PRIORITY[
            current["decision"]
        ]:
            photo_rows[row["source_path"]] = row
    for row in photo_rows.values():
        source = Path(row["source_path"])
        if is_raw_photo(row["source_path"]):
            if row["paired_jpeg_path"]:
                estimate += Path(row["paired_jpeg_path"]).stat().st_size
            else:
                raw_size = source.stat().st_size
                estimate += min(raw_size, max(1024 * 1024, raw_size // 3))
        else:
            estimate += source.stat().st_size
    return estimate


def human_size(byte_count: int) -> str:
    value = float(byte_count)
    for unit in ("bytes", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.0f} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def probe_media_info(source: Path, ffprobe: str) -> dict[str, object]:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(source),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        detail = result.stderr.strip() or "media metadata was unavailable"
        raise OSError(f"failed to inspect {source.name}: {detail[-500:]}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or "ffprobe failed"
        raise OSError(f"failed to inspect {source.name}: {detail[-500:]}")
    streams = payload.get("streams") or []
    video = next(
        (stream for stream in streams if stream.get("codec_type") == "video"),
        None,
    )
    if video is None:
        raise OSError(f"failed to inspect {source.name}: no video stream")
    audio = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"),
        None,
    )
    rotation = 0
    for side_data in video.get("side_data_list") or []:
        if "rotation" in side_data:
            rotation = int(round(float(side_data["rotation"]))) % 360
            break
    else:
        rotate_tag = (video.get("tags") or {}).get("rotate")
        if rotate_tag:
            rotation = int(round(float(rotate_tag))) % 360
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    if rotation in {90, 270}:
        display_width, display_height = height, width
    else:
        display_width, display_height = width, height
    duration_value = (payload.get("format") or {}).get("duration") or video.get(
        "duration"
    )
    try:
        duration = float(duration_value)
    except (TypeError, ValueError):
        duration = 0.0

    def stream_duration(stream: dict[str, object] | None) -> float:
        try:
            return float((stream or {}).get("duration") or 0)
        except (TypeError, ValueError):
            return 0.0

    color_transfer = str(video.get("color_transfer") or "").lower()
    hdr = color_transfer in {"arib-std-b67", "smpte2084"}
    average_rate = str(video.get("avg_frame_rate") or "")
    real_rate = str(video.get("r_frame_rate") or "")
    vfr = bool(average_rate and real_rate and average_rate != real_rate)
    return {
        "width": width,
        "height": height,
        "display_width": display_width,
        "display_height": display_height,
        "rotation": rotation,
        "hdr": hdr,
        "vfr": vfr,
        "color_transfer": color_transfer,
        "duration": duration,
        "video_duration": stream_duration(video),
        "audio_duration": stream_duration(audio),
        "video_codec": str(video.get("codec_name") or ""),
        "audio_codec": str((audio or {}).get("codec_name") or ""),
        "has_audio": audio is not None,
    }


def review_video_filter(source_info: dict[str, object]) -> str:
    filters: list[str] = []
    rotation = int(source_info["rotation"])
    if rotation == 90:
        filters.append("transpose=clock")
    elif rotation == 270:
        filters.append("transpose=cclock")
    elif rotation == 180:
        filters.extend(("hflip", "vflip"))
    if bool(source_info["hdr"]):
        filters.extend(
            (
                "zscale=t=linear:npl=100",
                "format=gbrpf32le",
                "tonemap=tonemap=hable:desat=0",
                "zscale=p=bt709:t=bt709:m=bt709:r=tv",
                "format=yuv420p",
            )
        )
    filters.append(
        (
            r"scale=w='if(gte(iw\,ih)\,min(iw\,1280)\,min(iw\,720))':"
            r"h='if(gte(iw\,ih)\,min(ih\,720)\,min(ih\,1280))':"
            "force_original_aspect_ratio=decrease:force_divisible_by=2"
        )
    )
    return ",".join(filters)


def run_ffmpeg_review_clip(
    source: Path,
    destination: Path,
    start_time: str,
    duration: float,
    ffmpeg: str,
    video_filter: str,
    source_rotation: int,
) -> None:
    input_options = ["-noautorotate"]
    if source_rotation:
        # We apply the probed display rotation explicitly in the filter chain.
        # Clearing it on input prevents ffmpeg from carrying the old display
        # matrix into the newly encoded, physically rotated review clip.
        input_options.extend(["-display_rotation:v:0", "0"])
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-ss",
            start_time,
            *input_options,
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-map_metadata",
            "-1",
            "-vf",
            video_filter,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "24",
            "-maxrate",
            "3M",
            "-bufsize",
            "6M",
            "-pix_fmt",
            "yuv420p",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-colorspace",
            "bt709",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-af",
            "aresample=async=1:first_pts=0",
            "-fps_mode",
            "vfr",
            "-movflags",
            "+faststart",
            "-metadata:s:v:0",
            "rotate=0",
            "-avoid_negative_ts",
            "make_zero",
            "-n",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not destination.is_file():
        destination.unlink(missing_ok=True)
        detail = result.stderr.strip() or "ffmpeg did not create the clip"
        raise OSError(f"failed to export review clip for {source.name}: {detail[-500:]}")


def validate_review_clip(
    destination: Path,
    source_info: dict[str, object],
    ffprobe: str,
) -> dict[str, object]:
    output_info = probe_media_info(destination, ffprobe)
    if output_info["video_codec"] != "h264":
        raise OSError(f"review clip is not H.264: {destination.name}")
    if bool(source_info["has_audio"]) and output_info["audio_codec"] != "aac":
        raise OSError(f"review clip audio is not AAC: {destination.name}")
    width = int(output_info["display_width"])
    height = int(output_info["display_height"])
    source_width = int(source_info["display_width"])
    source_height = int(source_info["display_height"])
    if width > source_width or height > source_height:
        raise OSError(f"review clip was unexpectedly upscaled: {destination.name}")
    if source_width >= source_height:
        if width > 1280 or height > 720 or width < height:
            raise OSError(f"review clip has invalid landscape dimensions: {destination.name}")
    elif width > 720 or height > 1280 or width >= height:
        raise OSError(f"review clip has invalid portrait dimensions: {destination.name}")
    if source_height and height:
        source_aspect = source_width / source_height
        output_aspect = width / height
        if abs(source_aspect - output_aspect) > 0.02:
            raise OSError(f"review clip aspect ratio changed: {destination.name}")
    if float(output_info["duration"]) <= 0:
        raise OSError(f"review clip is not playable: {destination.name}")
    video_duration = float(output_info["video_duration"])
    audio_duration = float(output_info["audio_duration"])
    if video_duration > 0 and audio_duration > 0:
        drift = abs(video_duration - audio_duration)
        if drift > 0.25:
            raise OSError(
                f"review clip audio/video duration drift is {drift:.3f}s: "
                f"{destination.name}"
            )
    if bool(source_info["hdr"]) and output_info["color_transfer"] != "bt709":
        raise OSError(f"HDR/HLG review clip was not tagged as BT.709: {destination.name}")
    return output_info


def export_clip(
    source: Path,
    destination: Path,
    start_time: str,
    end_time: str,
    ffmpeg: str,
    ffprobe: str,
) -> str:
    start_seconds = parse_timecode(start_time)
    end_seconds = parse_timecode(end_time)
    if end_seconds <= start_seconds:
        raise ValueError(
            f"clip end must be after start for {source.name}: {start_time} - {end_time}"
        )
    duration = end_seconds - start_seconds
    source_info = probe_media_info(source, ffprobe)
    video_filter = review_video_filter(source_info)
    special = []
    if int(source_info["rotation"]):
        special.append(f"rotation={source_info['rotation']}")
    if bool(source_info["hdr"]):
        special.append("HDR/HLG")
    if bool(source_info["vfr"]):
        special.append("VFR")
    if special:
        with tempfile.NamedTemporaryFile(
            prefix=".preflight-",
            suffix=".mp4",
            dir=destination.parent,
            delete=False,
        ) as handle:
            sample = Path(handle.name)
        sample.unlink()
        try:
            run_ffmpeg_review_clip(
                source,
                sample,
                start_time,
                min(duration, 2.0),
                ffmpeg,
                video_filter,
                int(source_info["rotation"]),
            )
            validate_review_clip(sample, source_info, ffprobe)
        finally:
            sample.unlink(missing_ok=True)
    run_ffmpeg_review_clip(
        source,
        destination,
        start_time,
        duration,
        ffmpeg,
        video_filter,
        int(source_info["rotation"]),
    )
    output_info = validate_review_clip(destination, source_info, ffprobe)
    dimensions = f"{output_info['display_width']}x{output_info['display_height']}"
    if special:
        return (
            f"Technical sample validated ({', '.join(special)}) before export; "
            f"final {dimensions} H.264/AAC clip verified."
        )
    return f"Final {dimensions} H.264/AAC review clip verified."


def build_review_set(
    rows: list[dict[str, str]],
    output: Path,
    mode: str,
    video_delivery: str,
    ffmpeg: str | None,
    ffprobe: str | None,
    raw_converter: str | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    output.mkdir(parents=True, exist_ok=True)
    for folder_name in CATEGORY_DIRS.values():
        (output / folder_name).mkdir(exist_ok=True)

    sources_with_clips = {
        row["source_path"]
        for row in rows
        if should_export_clip(row, video_delivery)
    }
    placement_decisions: dict[str, str] = {}
    placement_rows: dict[str, dict[str, str]] = {}
    for row in rows:
        decision = row["decision"]
        if decision == "excluded" or row["source_path"] in sources_with_clips:
            continue
        if (
            mode == "copy"
            and video_delivery == "timecodes"
            and is_video(row["source_path"])
        ):
            continue
        source_path = row["source_path"]
        current = placement_decisions.get(source_path)
        if current is None or CATEGORY_PRIORITY[decision] < CATEGORY_PRIORITY[current]:
            placement_decisions[source_path] = decision
            placement_rows[source_path] = row

    organized: dict[str, dict[str, str]] = {}
    if mode == "copy" and video_delivery == "timecodes":
        for row in rows:
            if row["decision"] == "excluded" or not is_video(row["source_path"]):
                continue
            organized[row["source_path"]] = {
                "organized_path": "",
                "review_source_path": row["source_path"],
                "review_asset_kind": "timecodes-only",
                "generation_status": "referenced",
                "generation_detail": (
                    "No whole high-bitrate video was copied; use the original for editing."
                ),
            }
    for source_path, decision in placement_decisions.items():
        source = Path(source_path)
        row = placement_rows[source_path]
        review_source = source
        review_kind = "source-link" if mode == "link" else "source-copy"
        status = "linked" if mode == "link" else "copied"
        filename = source.name
        convert_raw = False
        if mode == "copy" and is_raw_photo(source_path) and row["paired_jpeg_path"]:
            review_source = Path(row["paired_jpeg_path"])
            filename = f"{source.stem}__review{review_source.suffix.lower()}"
            review_kind = "paired-jpeg"
            status = "reused"
        elif mode == "copy" and is_raw_photo(source_path):
            review_source = source
            filename = f"{source.stem}__review.jpg"
            review_kind = "generated-jpeg"
            status = "generated"
            convert_raw = True
        destination = unique_destination(output / CATEGORY_DIRS[decision], filename)
        if convert_raw:
            if raw_converter is None:
                detail = (
                    "RAW converter unavailable. Install a supported converter "
                    "(ImageMagick, RawTherapee, darktable, or macOS sips) and "
                    "rerun with --raw-converter <path>."
                )
                organized[source_path] = {
                    "organized_path": "",
                    "review_source_path": str(source.resolve()),
                    "review_asset_kind": "not-generated",
                    "generation_status": "failed",
                    "generation_detail": detail,
                }
                continue
            try:
                convert_raw_to_jpeg(source, destination, raw_converter)
            except OSError as exc:
                detail = (
                    f"{exc}. Check RAW support, then rerun with "
                    "--raw-converter <path>."
                )
                organized[source_path] = {
                    "organized_path": "",
                    "review_source_path": str(source.resolve()),
                    "review_asset_kind": "not-generated",
                    "generation_status": "failed",
                    "generation_detail": detail,
                }
                continue
        else:
            place_media(review_source, destination, mode)
        if mode == "link":
            organized_path = str(destination.absolute())
        else:
            organized_path = str(destination.resolve(strict=False))
        organized[source_path] = {
            "organized_path": organized_path,
            "review_source_path": str(review_source.resolve()),
            "review_asset_kind": review_kind,
            "generation_status": status,
            "generation_detail": "",
        }

    exported_clips: dict[
        tuple[str, str, str, str], tuple[str, str, str, str]
    ] = {}
    for row in rows:
        if not should_export_clip(row, video_delivery):
            continue
        if ffmpeg is None:
            raise ValueError("ffmpeg is required for clip delivery")
        if ffprobe is None:
            raise ValueError("ffprobe is required for clip delivery")
        key = (
            row["source_path"],
            row["decision"],
            row["start_time"],
            row["end_time"],
        )
        if key in exported_clips:
            continue
        source = Path(row["source_path"])
        destination = unique_destination(
            output / CATEGORY_DIRS[row["decision"]],
            clip_filename(source, row["start_time"], row["end_time"]),
        )
        try:
            detail = export_clip(
                source,
                destination,
                row["start_time"],
                row["end_time"],
                ffmpeg,
                ffprobe,
            )
        except OSError as exc:
            destination.unlink(missing_ok=True)
            exported_clips[key] = (
                "",
                (
                    f"{exc}. No whole source video was copied. Verify ffmpeg/ffprobe "
                    "and rerun after checking a short technical sample."
                ),
                "not-generated",
                "failed",
            )
        else:
            exported_clips[key] = (
                str(destination.resolve(strict=False)),
                detail,
                "video-review-clip",
                "generated",
            )

    included_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []

    for row in rows:
        decision = row["decision"]
        if decision == "excluded":
            row["generation_status"] = "not-applicable"
            excluded_rows.append(row)
            continue

        result = dict(row)
        if should_export_clip(row, video_delivery):
            key = (
                row["source_path"],
                decision,
                row["start_time"],
                row["end_time"],
            )
            (
                result["organized_path"],
                result["generation_detail"],
                result["review_asset_kind"],
                result["generation_status"],
            ) = exported_clips[key]
            result["review_source_path"] = row["source_path"]
        else:
            result.update(organized.get(row["source_path"], {}))
        included_rows.append(result)

    return included_rows, excluded_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def timecode_text(row: dict[str, str]) -> str:
    start = row["start_time"]
    end = row["end_time"]
    if start and end:
        return f"{start} - {end}"
    return start or end or "整条素材"


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    included_rows: list[dict[str, str]],
    mode: str,
    video_delivery: str,
    estimated_bytes: int,
) -> None:
    counts = Counter(row["decision"] for row in rows)
    labels = {
        "select": "主选",
        "review": "备选_用户复筛",
        "memory": "纪念留档",
        "excluded": "排除",
    }
    lines = [
        "# 素材初筛报告",
        "",
        f"- 整理方式：{'建立链接' if mode == 'link' else '轻量审看副本'}",
        f"- 视频交付：{'裁切片段' if video_delivery == 'clips' else '仅标时间码'}",
        (
            f"- 生成前预估复筛占用：约 {human_size(estimated_bytes)} "
            f"({estimated_bytes} bytes)；这是估算且并非零占用"
        ),
        f"- 源文件总数：{len({row['source_path'] for row in rows})}",
        f"- 判断记录总数：{len(rows)}",
        f"- 主选记录：{counts['select']}",
        f"- 备选_用户复筛记录：{counts['review']}",
        f"- 纪念留档记录：{counts['memory']}",
        f"- 排除记录：{counts['excluded']}",
        "",
        (
            "原始素材未被移动、覆盖或删除；正式剪辑仍应使用原件。"
            "排除项只记录在清单中。"
        ),
        "",
        "## 入选素材与推荐片段",
        "",
    ]

    if video_delivery == "clips":
        lines[11:11] = [
            "- 裁切方式：约 720p H.264/AAC 轻量审看片段；不复制整条高码率原视频",
        ]

    if included_rows:
        for row in included_rows:
            reason = row["reason"] or "未填写理由"
            review_path = row["organized_path"] or "未生成（仅保留原件映射）"
            line = (
                f"- [{labels[row['decision']]}] 原件: {row['source_path']} | "
                f"审看: {review_path} | 类型: {row['review_asset_kind'] or '未指定'} | "
                f"{timecode_text(row)} | {reason}"
            )
            if row["generation_detail"]:
                line += f" | 处理说明: {row['generation_detail']}"
            lines.append(line)
    else:
        lines.append("- 无")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        rows = load_manifest(args.manifest)
        video_delivery = resolve_video_delivery(args.mode, args.video_delivery)
        if args.output.exists():
            if not args.output.is_dir():
                raise ValueError(f"output is not a directory: {args.output}")
            if any(args.output.iterdir()):
                raise ValueError(
                    f"output directory is not empty; choose a new directory: {args.output}"
                )
        clip_selection_rows_exist = video_delivery == "clips" and any(
            row["decision"] != "excluded"
            and is_video(row["source_path"])
            for row in rows
        )
        ffmpeg = (
            resolve_executable(args.ffmpeg, "ffmpeg")
            if clip_selection_rows_exist
            else None
        )
        ffprobe = (
            resolve_executable(args.ffprobe, "ffprobe")
            if clip_selection_rows_exist
            else None
        )
        if video_delivery == "clips" and ffprobe is not None:
            validate_clip_rows(rows, ffprobe)
        raw_converter = None
        if args.mode == "copy" and any(
            row["decision"] != "excluded"
            and is_raw_photo(row["source_path"])
            and not row["paired_jpeg_path"]
            for row in rows
        ):
            raw_converter = resolve_raw_converter(args.raw_converter)
        estimated_bytes = estimate_review_storage(rows, args.mode, video_delivery)
        print(
            "Estimated review-set storage before generation: "
            f"{estimated_bytes} bytes (~{human_size(estimated_bytes)}). "
            "This lightweight derivative set is not zero-storage."
        )
        included_rows, excluded_rows = build_review_set(
            rows,
            args.output.resolve(),
            args.mode,
            video_delivery,
            ffmpeg,
            ffprobe,
            raw_converter,
        )
        write_csv(args.output / "筛选清单.csv", included_rows)
        write_csv(args.output / "排除清单.csv", excluded_rows)
        write_report(
            args.output / "筛选报告.md",
            rows,
            included_rows,
            args.mode,
            video_delivery,
            estimated_bytes,
        )
        failed_count = sum(
            row["generation_status"] == "failed" for row in included_rows
        )
    except (OSError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if failed_count:
        print(
            f"created incomplete review set at {args.output.resolve()} "
            f"({failed_count} review assets were not generated); see 筛选报告.md",
            file=sys.stderr,
        )
        return 3
    print(
        f"created review set at {args.output.resolve()} "
        f"({len(included_rows)} included, {len(excluded_rows)} excluded)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
