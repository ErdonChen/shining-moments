#!/usr/bin/env python3
"""Build a non-destructive review set from a reviewed CSV manifest."""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
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
OUTPUT_FIELDS = [
    "source_path",
    "decision",
    "reason",
    "start_time",
    "end_time",
    "organized_path",
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
        choices=("timecodes", "clips"),
        default="timecodes",
        help="Keep whole video references with timecodes, or export selected intervals.",
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
    return parser.parse_args()


def normalize_decision(value: str, row_number: int) -> str:
    normalized = DECISION_ALIASES.get(value.strip().lower())
    if normalized is None:
        allowed = ", ".join(sorted(CATEGORY_DIRS | {"excluded"}))
        raise ValueError(
            f"row {row_number}: unsupported decision {value!r}; use one of {allowed}"
        )
    return normalized


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
            rows.append(
                {
                    "source_path": str(source),
                    "decision": decision,
                    "reason": reason,
                    "start_time": start_time,
                    "end_time": end_time,
                    "organized_path": "",
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


def should_export_clip(row: dict[str, str], video_delivery: str) -> bool:
    return (
        video_delivery == "clips"
        and row["decision"] in {"select", "review"}
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

    return f"{source.stem}__{safe(start_time)}_to_{safe(end_time)}{source.suffix}"


def resolve_executable(executable: str, label: str) -> str:
    if os.sep in executable:
        candidate = Path(executable).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise ValueError(f"{label} executable is unavailable: {candidate}")
        return str(candidate)
    resolved = shutil.which(executable)
    if resolved is None:
        raise ValueError(
            f"{label} is required for clip delivery; install it or use timecodes"
        )
    return resolved


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
        if row["decision"] not in {"select", "review"}:
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


def export_clip(
    source: Path,
    destination: Path,
    start_time: str,
    end_time: str,
    ffmpeg: str,
) -> None:
    start_seconds = parse_timecode(start_time)
    end_seconds = parse_timecode(end_time)
    if end_seconds <= start_seconds:
        raise ValueError(
            f"clip end must be after start for {source.name}: {start_time} - {end_time}"
        )
    duration = end_seconds - start_seconds
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-ss",
            start_time,
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-map",
            "0?",
            "-map_metadata",
            "0",
            "-c",
            "copy",
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
        detail = result.stderr.strip() or "ffmpeg did not create the clip"
        raise OSError(f"failed to cut {source.name}: {detail[-500:]}")


def build_review_set(
    rows: list[dict[str, str]],
    output: Path,
    mode: str,
    video_delivery: str,
    ffmpeg: str | None,
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
    for row in rows:
        decision = row["decision"]
        if decision == "excluded" or row["source_path"] in sources_with_clips:
            continue
        source_path = row["source_path"]
        current = placement_decisions.get(source_path)
        if current is None or CATEGORY_PRIORITY[decision] < CATEGORY_PRIORITY[current]:
            placement_decisions[source_path] = decision

    organized: dict[str, str] = {}
    for source_path, decision in placement_decisions.items():
        source = Path(source_path)
        destination = unique_destination(output / CATEGORY_DIRS[decision], source.name)
        place_media(source, destination, mode)
        if mode == "link":
            organized[source_path] = str(destination.absolute())
        else:
            organized[source_path] = str(destination.resolve(strict=False))

    exported_clips: dict[tuple[str, str, str, str], str] = {}
    for row in rows:
        if not should_export_clip(row, video_delivery):
            continue
        if ffmpeg is None:
            raise ValueError("ffmpeg is required for clip delivery")
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
        export_clip(
            source,
            destination,
            row["start_time"],
            row["end_time"],
            ffmpeg,
        )
        exported_clips[key] = str(destination.resolve(strict=False))

    included_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []

    for row in rows:
        decision = row["decision"]
        if decision == "excluded":
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
            result["organized_path"] = exported_clips[key]
        else:
            result["organized_path"] = organized.get(row["source_path"], "")
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
        f"- 整理方式：{'建立链接' if mode == 'link' else '复制素材'}",
        f"- 视频交付：{'裁切片段' if video_delivery == 'clips' else '仅标时间码'}",
        f"- 源文件总数：{len({row['source_path'] for row in rows})}",
        f"- 判断记录总数：{len(rows)}",
        f"- 主选记录：{counts['select']}",
        f"- 备选_用户复筛记录：{counts['review']}",
        f"- 纪念留档记录：{counts['memory']}",
        f"- 排除记录：{counts['excluded']}",
        "",
        "原始素材未被移动或删除。排除项只记录在清单中。",
        "",
        "## 入选素材与推荐片段",
        "",
    ]

    if video_delivery == "clips":
        lines[10:10] = [
            "- 裁切方式：保留源音视频流；片段边界可能对齐附近关键帧",
        ]

    if included_rows:
        for row in included_rows:
            source_name = Path(row["source_path"]).name
            reason = row["reason"] or "未填写理由"
            lines.append(
                f"- [{labels[row['decision']]}] {source_name} | "
                f"{timecode_text(row)} | {reason}"
            )
    else:
        lines.append("- 无")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        rows = load_manifest(args.manifest)
        if args.output.exists():
            if not args.output.is_dir():
                raise ValueError(f"output is not a directory: {args.output}")
            if any(args.output.iterdir()):
                raise ValueError(
                    f"output directory is not empty; choose a new directory: {args.output}"
                )
        clip_selection_rows_exist = args.video_delivery == "clips" and any(
            row["decision"] in {"select", "review"}
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
        if args.video_delivery == "clips" and ffprobe is not None:
            validate_clip_rows(rows, ffprobe)
        included_rows, excluded_rows = build_review_set(
            rows,
            args.output.resolve(),
            args.mode,
            args.video_delivery,
            ffmpeg,
        )
        write_csv(args.output / "筛选清单.csv", included_rows)
        write_csv(args.output / "排除清单.csv", excluded_rows)
        write_report(
            args.output / "筛选报告.md",
            rows,
            included_rows,
            args.mode,
            args.video_delivery,
        )
    except (OSError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        f"created review set at {args.output.resolve()} "
        f"({len(included_rows)} included, {len(excluded_rows)} excluded)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
