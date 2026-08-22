import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "build_review_set.py"


class BuildReviewSetTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        self.output = self.root / "review"

        self.select = self.sources / "select.jpg"
        self.review = self.sources / "review.mov"
        self.memory = self.sources / "memory.jpg"
        self.excluded = self.sources / "excluded.mov"
        for path in (self.select, self.review, self.memory, self.excluded):
            path.write_bytes(path.name.encode("utf-8"))

        self.duration_only_ffprobe = self.root / "duration_only_ffprobe.py"
        self.duration_only_ffprobe.write_text(
            "#!/usr/bin/env python3\nprint('600.0')\n",
            encoding="utf-8",
        )
        self.duration_only_ffprobe.chmod(0o755)

        self.manifest = self.root / "manifest.csv"
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": self.select,
                        "decision": "select",
                        "reason": "strong moment",
                        "start_time": "",
                        "end_time": "",
                    },
                    {
                        "source_path": self.review,
                        "decision": "review",
                        "reason": "usable duplicate",
                        "start_time": "00:03:12",
                        "end_time": "00:03:28",
                    },
                    {
                        "source_path": self.memory,
                        "decision": "memory",
                        "reason": "irreplaceable relationship",
                        "start_time": "",
                        "end_time": "",
                    },
                    {
                        "source_path": self.excluded,
                        "decision": "excluded",
                        "reason": "nothing recognizable",
                        "start_time": "",
                        "end_time": "",
                    },
                ]
            )

    def tearDown(self):
        self.tempdir.cleanup()

    def run_script(
        self,
        mode="link",
        video_delivery="timecodes",
        ffmpeg=None,
        ffprobe=None,
        raw_converter=None,
        select_ceiling=1.0,
        review_ceiling=1.0,
    ):
        command = [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(self.manifest),
            "--output",
            str(self.output),
            "--mode",
            mode,
        ]
        if video_delivery is not None:
            command.extend(["--video-delivery", video_delivery])
        if ffmpeg is not None:
            command.extend(["--ffmpeg", str(ffmpeg)])
        if ffprobe is None and video_delivery == "timecodes":
            ffprobe = self.duration_only_ffprobe
        if ffprobe is not None:
            command.extend(["--ffprobe", str(ffprobe)])
        if raw_converter is not None:
            command.extend(["--raw-converter", str(raw_converter)])
        if select_ceiling is not None:
            command.extend(["--select-ceiling", str(select_ceiling)])
        if review_ceiling is not None:
            command.extend(["--review-ceiling", str(review_ceiling)])
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

    def write_overflow_manifest(self, rows):
        fieldnames = [
            "source_path",
            "decision",
            "reason",
            "candidate_id",
            "similarity_group",
            "relationship_progression",
            "story_beat",
            "representative_score",
            "capture_style",
            "selection_evidence",
        ]
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def make_candidate(self, name, content=None):
        path = self.sources / name
        path.write_bytes(content if content is not None else name.encode("utf-8"))
        return path

    def read_output_csv(self, name):
        with (self.output / name).open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))

    def make_test_video(self, path, size):
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            self.skipTest("ffmpeg is unavailable")
        result = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"color=c=blue:s={size}:r=10",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=48000",
                "-t",
                "0.6",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-y",
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def probe_test_video(self, path):
        ffprobe = shutil.which("ffprobe")
        if ffprobe is None:
            self.skipTest("ffprobe is unavailable")
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,codec_name,width,height",
                "-of",
                "json",
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["streams"]

    def test_link_mode_organizes_without_copying_or_linking_excluded(self):
        result = self.run_script("link")
        self.assertEqual(result.returncode, 0, result.stderr)

        selected = self.output / "01_主选" / self.select.name
        review = self.output / "02_备选_用户复筛" / self.review.name
        memory = self.output / "03_纪念留档" / self.memory.name
        self.assertTrue(selected.is_symlink())
        self.assertTrue(review.is_symlink())
        self.assertTrue(memory.is_symlink())
        self.assertEqual(selected.resolve(), self.select.resolve())
        self.assertFalse((self.output / "04_排除" / self.excluded.name).exists())

        self.assertEqual(self.select.read_bytes(), b"select.jpg")
        self.assertTrue((self.output / "筛选清单.csv").exists())
        excluded_report = (self.output / "排除清单.csv").read_text(encoding="utf-8")
        self.assertIn("nothing recognizable", excluded_report)
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("00:03:12", report)
        self.assertIn("00:03:28", report)

    def test_copy_mode_copies_selected_files_and_keeps_sources(self):
        result = self.run_script("copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        copied = self.output / "01_主选" / self.select.name
        self.assertTrue(copied.is_file())
        self.assertFalse(copied.is_symlink())
        self.assertEqual(copied.read_bytes(), self.select.read_bytes())
        self.assertTrue(self.select.exists())

    def test_multiple_intervals_link_one_long_video_once(self):
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": self.review,
                        "decision": "review",
                        "reason": "first useful interval",
                        "start_time": "00:03:12",
                        "end_time": "00:03:28",
                    },
                    {
                        "source_path": self.review,
                        "decision": "review",
                        "reason": "second useful interval",
                        "start_time": "00:09:40",
                        "end_time": "00:09:55",
                    },
                ]
            )

        result = self.run_script("link")
        self.assertEqual(result.returncode, 0, result.stderr)
        review_files = list((self.output / "02_备选_用户复筛").iterdir())
        self.assertEqual(len(review_files), 1)
        self.assertTrue(review_files[0].is_symlink())
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("00:03:12", report)
        self.assertIn("00:09:40", report)

    def test_invalid_decision_fails_before_creating_review_set(self):
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.select,
                    "decision": "delete",
                    "reason": "unsafe request",
                }
            )

        result = self.run_script("link")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_copy_timecodes_maps_intervals_without_copying_whole_video(self):
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": self.review,
                        "decision": "select",
                        "reason": "strong stable interval",
                        "start_time": "00:01:00",
                        "end_time": "00:01:12",
                    },
                    {
                        "source_path": self.review,
                        "decision": "review",
                        "reason": "repairably shaky interval",
                        "start_time": "00:05:00",
                        "end_time": "00:05:08",
                    },
                    {
                        "source_path": self.review,
                        "decision": "excluded",
                        "reason": "unrecognizable interval",
                        "start_time": "00:08:00",
                        "end_time": "00:08:06",
                    },
                ]
            )

        result = self.run_script("copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        placed_files = [
            path
            for folder in ("01_主选", "02_备选_用户复筛", "03_纪念留档")
            for path in (self.output / folder).iterdir()
        ]
        self.assertEqual(placed_files, [])
        self.assertEqual(self.review.read_bytes(), b"review.mov")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["organized_path"] == "" for row in rows))
        self.assertTrue(
            all(row["review_asset_kind"] == "timecodes-only" for row in rows)
        )
        self.assertEqual(
            [(row["start_time"], row["end_time"]) for row in rows],
            [("00:01:00", "00:01:12"), ("00:05:00", "00:05:08")],
        )
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("源文件总数：1", report)
        self.assertIn("判断记录总数：3", report)

    def test_nonempty_output_directory_is_never_overwritten(self):
        self.output.mkdir()
        existing = self.output / "筛选报告.md"
        existing.write_text("existing report", encoding="utf-8")

        result = self.run_script("link")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(existing.read_text(encoding="utf-8"), "existing report")
        self.assertFalse((self.output / "01_主选").exists())

    def test_blank_reason_is_rejected(self):
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.excluded,
                    "decision": "excluded",
                    "reason": "",
                }
            )

        result = self.run_script("link")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_clip_delivery_exports_selected_intervals_without_copying_source(self):
        mock_ffmpeg = self.root / "mock_ffmpeg.py"
        mock_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'clip')\n",
            encoding="utf-8",
        )
        mock_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            "if '-show_streams' in sys.argv:\n"
            "    output = pathlib.Path(sys.argv[-1]).read_bytes() == b'clip'\n"
            "    width, height = ((1280, 720) if output else (1920, 1080))\n"
            "    print(json.dumps({'streams': ["
            "{'codec_type': 'video', 'codec_name': 'h264', 'width': width, "
            "'height': height, 'avg_frame_rate': '30/1', 'r_frame_rate': '30/1'}, "
            "{'codec_type': 'audio', 'codec_name': 'aac'}], "
            "'format': {'duration': '12.0'}}))\n"
            "else:\n"
            "    print('600.0')\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)

        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": self.review,
                        "decision": "select",
                        "reason": "strong interval",
                        "start_time": "00:01:00",
                        "end_time": "00:01:12",
                    },
                    {
                        "source_path": self.review,
                        "decision": "review",
                        "reason": "uncertain interval",
                        "start_time": "00:05:00",
                        "end_time": "00:05:08",
                    },
                    {
                        "source_path": self.review,
                        "decision": "memory",
                        "reason": "sentimental but not an edit clip",
                        "start_time": "00:06:00",
                        "end_time": "00:06:04",
                    },
                ]
            )

        result = self.run_script("copy", "clips", mock_ffmpeg, mock_ffprobe)
        self.assertEqual(result.returncode, 0, result.stderr)
        select_clips = list((self.output / "01_主选").iterdir())
        review_clips = list((self.output / "02_备选_用户复筛").iterdir())
        self.assertEqual(len(select_clips), 1)
        self.assertEqual(len(review_clips), 1)
        self.assertEqual(select_clips[0].read_bytes(), b"clip")
        self.assertEqual(review_clips[0].read_bytes(), b"clip")
        self.assertEqual(self.review.read_bytes(), b"review.mov")
        self.assertFalse((self.output / "01_主选" / self.review.name).exists())
        memory_clips = list((self.output / "03_纪念留档").iterdir())
        self.assertEqual(len(memory_clips), 1)
        self.assertEqual(memory_clips[0].read_bytes(), b"clip")
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("裁切片段", report)

    def test_clip_delivery_requires_timecodes_for_included_video(self):
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.review,
                    "decision": "review",
                    "reason": "whole video was not explicitly timed",
                    "start_time": "",
                    "end_time": "",
                }
            )

        result = self.run_script("link", "clips")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_clip_delivery_rejects_end_beyond_source_duration(self):
        mock_ffmpeg = self.root / "mock_ffmpeg.py"
        mock_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'clip')\n",
            encoding="utf-8",
        )
        mock_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\nprint('5.0')\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)

        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.review,
                    "decision": "select",
                    "reason": "invalid interval",
                    "start_time": "00:00:04",
                    "end_time": "00:00:07",
                }
            )

        result = self.run_script("copy", "clips", mock_ffmpeg, mock_ffprobe)
        self.assertNotEqual(result.returncode, 0)

    def test_copy_mode_reuses_manifest_paired_jpeg_for_raw_review(self):
        raw = self.sources / "portrait.cr3"
        raw.write_bytes(b"original-raw")
        paired = self.sources / "portrait-edit.jpg"
        paired.write_bytes(b"paired-jpeg")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                    "paired_jpeg_path",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "select",
                    "reason": "best expression",
                    "start_time": "",
                    "end_time": "",
                    "paired_jpeg_path": paired,
                }
            )

        result = self.run_script("copy", "timecodes")

        self.assertEqual(result.returncode, 0, result.stderr)
        review_files = list((self.output / "01_主选").iterdir())
        self.assertEqual(len(review_files), 1)
        self.assertEqual(review_files[0].suffix.lower(), ".jpg")
        self.assertEqual(review_files[0].read_bytes(), b"paired-jpeg")
        self.assertEqual(raw.read_bytes(), b"original-raw")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["source_path"], str(raw.resolve()))
        self.assertEqual(row["review_source_path"], str(paired.resolve()))
        self.assertEqual(row["review_asset_kind"], "paired-jpeg")
        self.assertEqual(row["generation_status"], "reused")
        self.assertEqual(Path(row["organized_path"]).resolve(), review_files[0].resolve())

    def test_copy_mode_auto_reuses_same_stem_jpeg_for_raw_review(self):
        raw = self.sources / "family.NEF"
        raw.write_bytes(b"original-raw")
        paired = self.sources / "family.JPG"
        paired.write_bytes(b"same-stem-jpeg")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "review",
                    "reason": "relationship moment",
                }
            )

        result = self.run_script("copy", "timecodes")

        self.assertEqual(result.returncode, 0, result.stderr)
        review_files = list((self.output / "02_备选_用户复筛").iterdir())
        self.assertEqual(len(review_files), 1)
        self.assertEqual(review_files[0].suffix.lower(), ".jpg")
        self.assertEqual(review_files[0].read_bytes(), b"same-stem-jpeg")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["paired_jpeg_path"], str(paired.resolve()))
        self.assertEqual(row["review_asset_kind"], "paired-jpeg")

    def test_copy_mode_converts_unpaired_raw_to_jpeg_review_copy(self):
        raw = self.sources / "solo.RAF"
        raw.write_bytes(b"original-raw")
        converter = self.root / "mock_raw_converter.py"
        converter.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'generated-jpeg')\n",
            encoding="utf-8",
        )
        converter.chmod(0o755)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "select",
                    "reason": "unique portrait",
                }
            )

        result = self.run_script(
            "copy", "timecodes", raw_converter=converter
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        review_files = list((self.output / "01_主选").iterdir())
        self.assertEqual(len(review_files), 1)
        self.assertEqual(review_files[0].suffix.lower(), ".jpg")
        self.assertEqual(review_files[0].read_bytes(), b"generated-jpeg")
        self.assertEqual(raw.read_bytes(), b"original-raw")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["review_source_path"], str(raw.resolve()))
        self.assertEqual(row["review_asset_kind"], "generated-jpeg")
        self.assertEqual(row["generation_status"], "generated")

    def test_raw_conversion_failure_is_reported_without_copying_raw(self):
        raw = self.sources / "unreadable.CR2"
        raw.write_bytes(b"original-raw")
        converter = self.root / "failing_raw_converter.py"
        converter.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "print('decoder missing camera profile', file=sys.stderr)\n"
            "raise SystemExit(7)\n",
            encoding="utf-8",
        )
        converter.chmod(0o755)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "review",
                    "reason": "keep for human review",
                }
            )

        result = self.run_script(
            "copy", "timecodes", raw_converter=converter
        )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(raw.read_bytes(), b"original-raw")
        self.assertEqual(list((self.output / "02_备选_用户复筛").iterdir()), [])
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["review_asset_kind"], "not-generated")
        self.assertEqual(row["generation_status"], "failed")
        self.assertEqual(row["organized_path"], "")
        self.assertIn("decoder missing camera profile", row["generation_detail"])
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn(str(raw.resolve()), report)
        self.assertIn("--raw-converter", report)

    def test_copy_mode_defaults_to_candidate_clips_instead_of_whole_video(self):
        mock_ffmpeg = self.root / "mock_ffmpeg.py"
        mock_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'review-clip')\n",
            encoding="utf-8",
        )
        mock_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            "if '-show_streams' in sys.argv:\n"
            "    output = pathlib.Path(sys.argv[-1]).read_bytes() == b'review-clip'\n"
            "    width, height = ((1280, 720) if output else (1920, 1080))\n"
            "    print(json.dumps({'streams': ["
            "{'codec_type': 'video', 'codec_name': 'h264', 'width': width, "
            "'height': height, 'avg_frame_rate': '30/1', 'r_frame_rate': '30/1'}, "
            "{'codec_type': 'audio', 'codec_name': 'aac'}], "
            "'format': {'duration': '12.0'}}))\n"
            "else:\n"
            "    print('600.0')\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.review,
                    "decision": "select",
                    "reason": "best twelve seconds",
                    "start_time": "00:01:00",
                    "end_time": "00:01:12",
                }
            )

        result = self.run_script(
            "copy", None, mock_ffmpeg, mock_ffprobe
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        review_files = list((self.output / "01_主选").iterdir())
        self.assertEqual(len(review_files), 1)
        self.assertEqual(review_files[0].read_bytes(), b"review-clip")
        self.assertFalse((self.output / "01_主选" / self.review.name).exists())
        self.assertEqual(self.review.read_bytes(), b"review.mov")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["review_asset_kind"], "video-review-clip")
        self.assertEqual(row["start_time"], "00:01:00")
        self.assertEqual(row["end_time"], "00:01:12")

    def test_real_high_resolution_candidate_clips_are_720p_h264_aac(self):
        hd = self.sources / "hd.mp4"
        uhd = self.sources / "uhd.mp4"
        self.make_test_video(hd, "1920x1080")
        self.make_test_video(uhd, "3840x2160")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": hd,
                        "decision": "select",
                        "reason": "HD candidate",
                        "start_time": "00:00:00",
                        "end_time": "00:00:00.5",
                    },
                    {
                        "source_path": uhd,
                        "decision": "review",
                        "reason": "4K candidate",
                        "start_time": "00:00:00",
                        "end_time": "00:00:00.5",
                    },
                ]
            )

        result = self.run_script("copy", "clips")

        self.assertEqual(result.returncode, 0, result.stderr)
        clips = [
            next((self.output / "01_主选").iterdir()),
            next((self.output / "02_备选_用户复筛").iterdir()),
        ]
        for clip in clips:
            with self.subTest(clip=clip.name):
                streams = self.probe_test_video(clip)
                video = next(stream for stream in streams if stream["codec_type"] == "video")
                audio = next(stream for stream in streams if stream["codec_type"] == "audio")
                self.assertEqual((video["width"], video["height"]), (1280, 720))
                self.assertEqual(video["codec_name"], "h264")
                self.assertEqual(audio["codec_name"], "aac")
                self.assertEqual(clip.suffix.lower(), ".mp4")
        self.assertTrue(hd.exists())
        self.assertTrue(uhd.exists())

    def test_real_low_resolution_candidate_clip_is_not_upscaled(self):
        low = self.sources / "low.mp4"
        self.make_test_video(low, "640x360")
        source_before = low.read_bytes()
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": low,
                    "decision": "select",
                    "reason": "already small enough",
                    "start_time": "00:00:00",
                    "end_time": "00:00:00.5",
                }
            )

        result = self.run_script("copy", "clips")

        self.assertEqual(result.returncode, 0, result.stderr)
        clip = next((self.output / "01_主选").iterdir())
        streams = self.probe_test_video(clip)
        video = next(stream for stream in streams if stream["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (640, 360))
        self.assertEqual(low.read_bytes(), source_before)

    def test_real_portrait_candidate_preserves_orientation_at_720p(self):
        portrait = self.sources / "portrait.mp4"
        self.make_test_video(portrait, "1080x1920")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": portrait,
                    "decision": "review",
                    "reason": "vertical relationship moment",
                    "start_time": "00:00:00",
                    "end_time": "00:00:00.5",
                }
            )

        result = self.run_script("copy", "clips")

        self.assertEqual(result.returncode, 0, result.stderr)
        clip = next((self.output / "02_备选_用户复筛").iterdir())
        streams = self.probe_test_video(clip)
        video = next(stream for stream in streams if stream["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (720, 1280))
        self.assertGreater(video["height"], video["width"])

    def test_rotation_metadata_triggers_sample_validation_before_export(self):
        base = self.sources / "rotation-base.mp4"
        rotated = self.sources / "rotation-tagged.mp4"
        self.make_test_video(base, "1920x1080")
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            self.skipTest("ffmpeg is unavailable")
        tag_result = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-display_rotation:v:0",
                "90",
                "-i",
                str(base),
                "-c",
                "copy",
                "-y",
                str(rotated),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(tag_result.returncode, 0, tag_result.stderr)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": rotated,
                    "decision": "select",
                    "reason": "portrait display orientation",
                    "start_time": "00:00:00",
                    "end_time": "00:00:00.5",
                }
            )

        result = self.run_script("copy", "clips")

        self.assertEqual(result.returncode, 0, result.stderr)
        clip = next((self.output / "01_主选").iterdir())
        streams = self.probe_test_video(clip)
        video = next(stream for stream in streams if stream["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (720, 1280))
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertIn("rotation", row["generation_detail"].lower())
        self.assertIn("sample", row["generation_detail"].lower())
        self.assertFalse(any(path.name.startswith(".preflight-") for path in clip.parent.iterdir()))

    def test_unavailable_raw_converter_is_recorded_as_partial_failure(self):
        raw = self.sources / "unsupported.nef"
        raw.write_bytes(b"original-raw")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "review",
                    "reason": "meaningful frame",
                }
            )

        result = self.run_script(
            "copy",
            "timecodes",
            raw_converter=self.root / "missing-converter",
        )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(raw.read_bytes(), b"original-raw")
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["generation_status"], "failed")
        self.assertEqual(row["review_asset_kind"], "not-generated")
        self.assertIn("RAW converter unavailable", row["generation_detail"])

    def test_video_export_failure_is_recorded_without_copying_whole_source(self):
        failing_ffmpeg = self.root / "failing_ffmpeg.py"
        failing_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "print('encoder unavailable', file=sys.stderr)\n"
            "raise SystemExit(7)\n",
            encoding="utf-8",
        )
        failing_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "if '-show_streams' in sys.argv:\n"
            "    print(json.dumps({'streams': ["
            "{'codec_type': 'video', 'codec_name': 'h264', 'width': 1920, "
            "'height': 1080, 'avg_frame_rate': '30/1', 'r_frame_rate': '30/1'}, "
            "{'codec_type': 'audio', 'codec_name': 'aac'}], "
            "'format': {'duration': '600.0'}}))\n"
            "else:\n"
            "    print('600.0')\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)
        original = self.review.read_bytes()
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": self.review,
                    "decision": "select",
                    "reason": "candidate interval",
                    "start_time": "00:01:00",
                    "end_time": "00:01:12",
                }
            )

        result = self.run_script("copy", "clips", failing_ffmpeg, mock_ffprobe)

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(self.review.read_bytes(), original)
        self.assertEqual(list((self.output / "01_主选").iterdir()), [])
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["generation_status"], "failed")
        self.assertEqual(row["review_asset_kind"], "not-generated")
        self.assertIn("encoder unavailable", row["generation_detail"])
        self.assertIn(str(self.review.resolve()), row["source_path"])

    def test_copy_clips_exports_memory_interval_but_never_excluded_video(self):
        memory_video = self.sources / "family-memory.mp4"
        excluded_video = self.sources / "excluded-video.mp4"
        self.make_test_video(memory_video, "1920x1080")
        self.make_test_video(excluded_video, "1920x1080")
        excluded_before = excluded_video.read_bytes()
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "source_path": memory_video,
                        "decision": "memory",
                        "reason": "irreplaceable family moment",
                        "start_time": "00:00:00",
                        "end_time": "00:00:00.5",
                    },
                    {
                        "source_path": excluded_video,
                        "decision": "excluded",
                        "reason": "unrecognizable and no known memory value",
                        "start_time": "",
                        "end_time": "",
                    },
                ]
            )

        result = self.run_script("copy", "clips")

        self.assertEqual(result.returncode, 0, result.stderr)
        memory_files = list((self.output / "03_纪念留档").iterdir())
        self.assertEqual(len(memory_files), 1)
        self.assertEqual(memory_files[0].suffix, ".mp4")
        self.assertFalse((self.output / "03_纪念留档" / memory_video.name).exists())
        self.assertEqual(excluded_video.read_bytes(), excluded_before)
        self.assertFalse(any(path.name == excluded_video.name for path in self.output.rglob("*")))

    def test_copy_mode_estimates_nonzero_review_storage_before_generation(self):
        raw = self.sources / "trip.cr3"
        paired = self.sources / "trip.jpg"
        raw.write_bytes(b"r" * 1000)
        paired.write_bytes(b"j" * 200)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "paired_jpeg_path",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": raw,
                    "decision": "select",
                    "reason": "strong travel frame",
                    "paired_jpeg_path": paired,
                }
            )

        result = self.run_script("copy", "timecodes")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(
            result.stdout,
            r"Estimated review-set storage before generation: [1-9][0-9]* bytes",
        )
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("生成前预估复筛占用", report)
        self.assertIn("并非零占用", report)

    def test_same_named_sources_receive_stable_non_overwriting_destinations(self):
        first_dir = self.sources / "first"
        second_dir = self.sources / "second"
        first_dir.mkdir()
        second_dir.mkdir()
        first = first_dir / "same.jpg"
        second = second_dir / "same.jpg"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["source_path", "decision", "reason"],
            )
            writer.writeheader()
            writer.writerows(
                [
                    {"source_path": first, "decision": "select", "reason": "one"},
                    {"source_path": second, "decision": "select", "reason": "two"},
                ]
            )

        result = self.run_script("copy", "timecodes")

        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = sorted((self.output / "01_主选").iterdir())
        self.assertEqual([path.name for path in outputs], ["same.jpg", "same__2.jpg"])
        self.assertEqual({path.read_bytes() for path in outputs}, {b"first", b"second"})

    def test_hdr_vfr_source_uses_sample_validation_and_bt709_filter(self):
        source = self.sources / "hdr-vfr.mov"
        source.write_bytes(b"source")
        invocation_log = self.root / "ffmpeg-invocations.txt"
        mock_ffmpeg = self.root / "mock_ffmpeg.py"
        mock_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            f"log = pathlib.Path({str(invocation_log)!r})\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write(' '.join(sys.argv[1:]) + '\\n')\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'output')\n",
            encoding="utf-8",
        )
        mock_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            "if '-show_streams' not in sys.argv:\n"
            "    print('10.0')\n"
            "else:\n"
            "    output = pathlib.Path(sys.argv[-1]).read_bytes() == b'output'\n"
            "    video = {'codec_type': 'video', 'codec_name': 'h264', "
            "'width': 1280 if output else 3840, 'height': 720 if output else 2160, "
            "'avg_frame_rate': '30/1' if output else '24000/1001', "
            "'r_frame_rate': '30/1', "
            "'color_transfer': 'bt709' if output else 'arib-std-b67'}\n"
            "    print(json.dumps({'streams': [video, "
            "{'codec_type': 'audio', 'codec_name': 'aac'}], "
            "'format': {'duration': '2.0'}}))\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": source,
                    "decision": "review",
                    "reason": "technical validation candidate",
                    "start_time": "00:00:00",
                    "end_time": "00:00:02",
                }
            )

        result = self.run_script("copy", "clips", mock_ffmpeg, mock_ffprobe)

        self.assertEqual(result.returncode, 0, result.stderr)
        invocations = invocation_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(invocations), 2)
        self.assertTrue(all("tonemap=" in invocation for invocation in invocations))
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertIn("HDR/HLG", row["generation_detail"])
        self.assertIn("VFR", row["generation_detail"])
        self.assertIn("sample", row["generation_detail"].lower())

    def test_special_video_sample_rejects_audio_video_duration_drift(self):
        source = self.sources / "vfr-sync.mov"
        source.write_bytes(b"source")
        mock_ffmpeg = self.root / "mock_ffmpeg.py"
        mock_ffmpeg.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1]).write_bytes(b'output')\n",
            encoding="utf-8",
        )
        mock_ffmpeg.chmod(0o755)
        mock_ffprobe = self.root / "mock_ffprobe.py"
        mock_ffprobe.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            "if '-show_streams' not in sys.argv:\n"
            "    print('10.0')\n"
            "else:\n"
            "    output = pathlib.Path(sys.argv[-1]).read_bytes() == b'output'\n"
            "    video = {'codec_type': 'video', 'codec_name': 'h264', "
            "'width': 1280 if output else 1920, 'height': 720 if output else 1080, "
            "'duration': '2.0', 'avg_frame_rate': '30/1' if output else '24000/1001', "
            "'r_frame_rate': '30/1'}\n"
            "    audio = {'codec_type': 'audio', 'codec_name': 'aac', "
            "'duration': '0.5' if output else '2.0'}\n"
            "    print(json.dumps({'streams': [video, audio], "
            "'format': {'duration': '2.0'}}))\n",
            encoding="utf-8",
        )
        mock_ffprobe.chmod(0o755)
        with self.manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_path",
                    "decision",
                    "reason",
                    "start_time",
                    "end_time",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "source_path": source,
                    "decision": "review",
                    "reason": "check VFR synchronization",
                    "start_time": "00:00:00",
                    "end_time": "00:00:02",
                }
            )

        result = self.run_script("copy", "clips", mock_ffmpeg, mock_ffprobe)

        self.assertEqual(result.returncode, 3, result.stderr)
        with (self.output / "筛选清单.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["generation_status"], "failed")
        self.assertIn("audio/video duration drift", row["generation_detail"])

    def test_review_ceiling_leaves_natural_twelve_percent_review_set_unchanged(self):
        rows = []
        for index in range(25):
            source = self.make_candidate(f"natural-{index:02d}.jpg")
            rows.append(
                {
                    "source_path": source,
                    "decision": "review" if index < 3 else "select",
                    "reason": "distinct useful alternative" if index < 3 else "strongest frame",
                    "candidate_id": f"natural-{index:02d}",
                    "similarity_group": "",
                    "relationship_progression": "",
                    "story_beat": "",
                    "representative_score": str(100 - index),
                    "capture_style": "documentary",
                    "selection_evidence": "distinct scene",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.2)

        self.assertEqual(result.returncode, 0, result.stderr)
        screening = self.read_output_csv("筛选清单.csv")
        not_selected = self.read_output_csv("未入选清单.csv")
        self.assertEqual(sum(row["decision"] == "review" for row in screening), 3)
        self.assertEqual(not_selected, [])
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("唯一候选数（照片）：25", report)
        self.assertIn("备选比例（照片）：12.00%", report)
        self.assertIn("溢出精简（照片）：未触发", report)

    def test_default_select_trigger_runs_above_ten_percent(self):
        rows = []
        for index in range(20):
            source = self.make_candidate(f"primary-default-{index:02d}.jpg")
            rows.append(
                {
                    "source_path": source,
                    "decision": "select" if index < 8 else "excluded",
                    "reason": "ordinary first-pass choice",
                    "candidate_id": f"primary-default-{index:02d}",
                    "similarity_group": "",
                    "relationship_progression": "false",
                    "story_beat": "",
                    "representative_score": str(80 - index),
                    "capture_style": "documentary",
                    "selection_evidence": "",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(select_ceiling=None, review_ceiling=1.0)

        self.assertEqual(result.returncode, 0, result.stderr)
        screening = self.read_output_csv("筛选清单.csv")
        self.assertEqual(sum(row["decision"] == "select" for row in screening), 2)
        self.assertEqual(sum(row["decision"] == "review" for row in screening), 6)
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("主选软触发线：10.00%", report)

    def test_review_overflow_reduces_redundant_burst_below_default_ceiling(self):
        rows = []
        for index in range(20):
            source = self.make_candidate(f"burst-{index:02d}.jpg")
            is_review = index < 11
            rows.append(
                {
                    "source_path": source,
                    "decision": "review" if is_review else "select",
                    "reason": "usable same-person burst" if is_review else "different selected scene",
                    "candidate_id": f"burst-{index:02d}",
                    "similarity_group": "same-person-burst" if is_review else "",
                    "relationship_progression": "false",
                    "story_beat": "same beat" if is_review else "",
                    "representative_score": str(100 - index),
                    "capture_style": "posed" if is_review else "documentary",
                    "selection_evidence": "minor timing variation" if is_review else "distinct scene",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=None)

        self.assertEqual(result.returncode, 0, result.stderr)
        screening = self.read_output_csv("筛选清单.csv")
        not_selected = self.read_output_csv("未入选清单.csv")
        retained_review = [row for row in screening if row["decision"] == "review"]
        self.assertLessEqual(len(retained_review), 5)
        self.assertGreaterEqual(len(not_selected), 6)
        self.assertTrue(all(row["decision"] == "not_selected" for row in not_selected))
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("备选比例（照片）：55.00%", report)
        self.assertIn("溢出精简（照片）：已触发", report)

    def test_posed_group_overflow_keeps_best_face_and_gaze_representative(self):
        candidates = [
            ("group-blink.jpg", 55, "closed eyes"),
            ("group-blocked.jpg", 60, "face obstructed"),
            ("group-flat.jpg", 70, "flat expression"),
            ("group-looking-away.jpg", 75, "unsuitable gaze"),
            ("group-open-natural.jpg", 99, "open eyes; visible faces; natural expression; camera-facing gaze"),
        ]
        rows = []
        for name, score, evidence in candidates:
            rows.append(
                {
                    "source_path": self.make_candidate(name),
                    "decision": "review",
                    "reason": "posed group burst",
                    "candidate_id": name,
                    "similarity_group": "posed-group-01",
                    "relationship_progression": "false",
                    "story_beat": "posed group",
                    "representative_score": str(score),
                    "capture_style": "posed",
                    "selection_evidence": evidence,
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.2)

        self.assertEqual(result.returncode, 0, result.stderr)
        retained = [
            Path(row["source_path"]).name
            for row in self.read_output_csv("筛选清单.csv")
            if row["decision"] == "review"
        ]
        self.assertEqual(retained, ["group-open-natural.jpg"])

    def test_candid_family_overflow_prefers_emotional_story_over_direct_gaze(self):
        candidates = [
            ("family-camera-gaze.jpg", 72, "direct gaze but weak interaction"),
            ("family-embrace.jpg", 98, "strong relationship, emotion, and story beat"),
            ("family-neutral.jpg", 50, "neutral expression"),
            ("family-repeat.jpg", 45, "repeated interaction"),
            ("family-obstructed.jpg", 40, "obstructed moment"),
        ]
        rows = []
        for name, score, evidence in candidates:
            rows.append(
                {
                    "source_path": self.make_candidate(name),
                    "decision": "review",
                    "reason": "candid family burst",
                    "candidate_id": name,
                    "similarity_group": "candid-family-01",
                    "relationship_progression": "false",
                    "story_beat": "same interaction",
                    "representative_score": str(score),
                    "capture_style": "candid",
                    "selection_evidence": evidence,
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.2)

        self.assertEqual(result.returncode, 0, result.stderr)
        retained = [
            Path(row["source_path"]).name
            for row in self.read_output_csv("筛选清单.csv")
            if row["decision"] == "review"
        ]
        self.assertEqual(retained, ["family-embrace.jpg"])

    def test_memory_cannot_absorb_overflow_and_not_selected_stays_distinct_from_excluded(self):
        rows = []
        decisions = ["select"] + ["review"] * 6 + ["memory"] * 2 + ["excluded"]
        for index, decision in enumerate(decisions):
            source = self.make_candidate(f"boundary-{index:02d}.jpg")
            rows.append(
                {
                    "source_path": source,
                    "decision": decision,
                    "reason": "corrupt" if decision == "excluded" else "relationship" if decision == "memory" else "candidate",
                    "candidate_id": f"boundary-{index:02d}",
                    "similarity_group": "overflow-burst" if decision == "review" else "",
                    "relationship_progression": "false",
                    "story_beat": "same beat" if decision == "review" else "",
                    "representative_score": str(100 - index),
                    "capture_style": "documentary",
                    "selection_evidence": "",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.2)

        self.assertEqual(result.returncode, 0, result.stderr)
        screening = self.read_output_csv("筛选清单.csv")
        not_selected = self.read_output_csv("未入选清单.csv")
        excluded = self.read_output_csv("排除清单.csv")
        self.assertEqual(sum(row["decision"] == "memory" for row in screening), 2)
        self.assertEqual(sum(row["decision"] == "review" for row in screening), 2)
        self.assertEqual(len(not_selected), 4)
        self.assertTrue(all(row["decision"] == "not_selected" for row in not_selected))
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["decision"], "excluded")
        for row in not_selected:
            self.assertEqual(row["organized_path"], "")

    def test_unique_candidate_denominator_collapses_raw_pairs_and_exact_duplicates(self):
        raw = self.make_candidate("paired.dng", b"raw")
        jpeg = self.make_candidate("paired.jpg", b"jpeg")
        duplicate_a = self.make_candidate("duplicate-a.jpg", b"same bytes")
        duplicate_b = self.make_candidate("duplicate-b.jpg", b"same bytes")
        rows = []
        for source, candidate_id in (
            (raw, ""),
            (jpeg, ""),
            (duplicate_a, ""),
            (duplicate_b, ""),
        ):
            rows.append(
                {
                    "source_path": source,
                    "decision": "review",
                    "reason": "dedup denominator check",
                    "candidate_id": candidate_id,
                    "similarity_group": "",
                    "relationship_progression": "false",
                    "story_beat": "",
                    "representative_score": "80",
                    "capture_style": "documentary",
                    "selection_evidence": "",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.5)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("唯一候选数（照片）：2", report)
        self.assertIn("备选比例（照片）：100.00%", report)
        retained_review = [
            row
            for row in self.read_output_csv("筛选清单.csv")
            if row["decision"] == "review"
        ]
        self.assertLessEqual(len({row["candidate_id"] or row["source_path"] for row in retained_review}), 1)

    def test_user_supplied_review_ceiling_is_conditional_not_a_fill_target(self):
        rows = []
        for index in range(10):
            source = self.make_candidate(f"custom-{index:02d}.jpg")
            rows.append(
                {
                    "source_path": source,
                    "decision": "review" if index < 3 else "select",
                    "reason": "genuinely distinct alternative" if index < 3 else "selected",
                    "candidate_id": f"custom-{index:02d}",
                    "similarity_group": "",
                    "relationship_progression": "false",
                    "story_beat": "",
                    "representative_score": str(100 - index),
                    "capture_style": "documentary",
                    "selection_evidence": "distinct scene",
                }
            )
        self.write_overflow_manifest(rows)

        result = self.run_script(review_ceiling=0.4)

        self.assertEqual(result.returncode, 0, result.stderr)
        screening = self.read_output_csv("筛选清单.csv")
        self.assertEqual(sum(row["decision"] == "review" for row in screening), 3)
        self.assertEqual(self.read_output_csv("未入选清单.csv"), [])
        report = (self.output / "筛选报告.md").read_text(encoding="utf-8")
        self.assertIn("备选软触发线：40.00%", report)
        self.assertIn("溢出精简（照片）：未触发", report)


if __name__ == "__main__":
    unittest.main()
