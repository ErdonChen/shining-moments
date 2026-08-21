import csv
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
            "--video-delivery",
            video_delivery,
        ]
        if ffmpeg is not None:
            command.extend(["--ffmpeg", str(ffmpeg)])
        if ffprobe is not None:
            command.extend(["--ffprobe", str(ffprobe)])
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

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

    def test_mixed_interval_decisions_copy_one_long_video_once(self):
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
        self.assertEqual(len(placed_files), 1)
        self.assertEqual(placed_files[0].parent.name, "01_主选")
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
            "#!/usr/bin/env python3\nprint('600.0')\n",
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
        self.assertEqual(list((self.output / "03_纪念留档").iterdir()), [])
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


if __name__ == "__main__":
    unittest.main()
