import importlib.util
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "build_review_set.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("review_builder_guardrails", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SelectionGuardrailTests(unittest.TestCase):
    def setUp(self):
        self.builder = load_builder()
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def row(
        self,
        path,
        decision,
        *,
        score=50,
        evidence="",
        story_beat="",
        start="",
        end="",
        similarity_group="",
    ):
        return {
            "source_path": str(path),
            "decision": decision,
            "reason": "first-pass judgment",
            "start_time": start,
            "end_time": end,
            "paired_jpeg_path": "",
            "candidate_id": path.name,
            "similarity_group": similarity_group,
            "relationship_progression": "false",
            "story_beat": story_beat,
            "representative_score": str(score),
            "capture_style": "documentary",
            "selection_evidence": evidence,
            "first_pass_decision": decision,
            "overflow_action": "",
            "organized_path": "",
            "review_source_path": "",
            "review_asset_kind": "",
            "generation_status": "",
            "generation_detail": "",
        }

    def photo_rows(self, select_count, review_count, total=20, protected_select=0):
        rows = []
        for index in range(total):
            path = self.root / f"photo-{index:02d}.jpg"
            path.write_bytes(path.name.encode())
            if index < select_count:
                decision = "select"
            elif index < select_count + review_count:
                decision = "review"
            else:
                decision = "excluded"
            protected = decision == "select" and index < protected_select
            rows.append(
                self.row(
                    path,
                    decision,
                    score=95 if protected else 60,
                    evidence="distinct high-quality story moment" if protected else "",
                    story_beat=f"beat-{index}" if protected else "",
                )
            )
        return rows

    def test_photo_guardrail_demotes_select_then_review_without_using_memory(self):
        rows = self.photo_rows(select_count=8, review_count=8)

        stats = self.builder.apply_selection_guardrails(
            rows,
            select_ceiling=0.10,
            review_ceiling=0.25,
            video_durations={},
            short_video_seconds=60,
        )

        self.assertTrue(stats["photo"]["triggered"])
        self.assertEqual(sum(row["decision"] == "select" for row in rows), 2)
        self.assertEqual(sum(row["decision"] == "review" for row in rows), 5)
        self.assertEqual(sum(row["decision"] == "memory" for row in rows), 0)
        self.assertEqual(sum(row["decision"] == "not_selected" for row in rows), 9)

    def test_photo_guardrail_keeps_evidenced_nonredundant_quality_overflow(self):
        rows = self.photo_rows(
            select_count=5,
            review_count=0,
            protected_select=5,
        )

        stats = self.builder.apply_selection_guardrails(
            rows,
            select_ceiling=0.10,
            review_ceiling=0.25,
            video_durations={},
            short_video_seconds=60,
        )

        self.assertEqual(sum(row["decision"] == "select" for row in rows), 5)
        self.assertGreater(stats["photo"]["final_select_ratio"], 0.10)
        self.assertEqual(stats["photo"]["retained_exception_count"], 5)

    def test_video_ratios_use_interval_unions_and_source_duration(self):
        video = self.root / "long.mp4"
        video.write_bytes(b"video")
        rows = [
            self.row(video, "select", start="00:00:00", end="00:00:20"),
            self.row(video, "select", start="00:00:10", end="00:00:30"),
            self.row(video, "review", start="00:00:30", end="00:01:10"),
        ]

        stats = self.builder.apply_selection_guardrails(
            rows,
            select_ceiling=0.10,
            review_ceiling=0.25,
            video_durations={str(video): 100.0},
            short_video_seconds=60,
        )

        self.assertEqual(stats["video"]["total_duration"], 100.0)
        self.assertEqual(stats["video"]["initial_select_duration"], 30.0)
        self.assertEqual(stats["video"]["initial_review_duration"], 40.0)
        self.assertLessEqual(stats["video"]["final_select_duration"], 20.0)
        self.assertLessEqual(stats["video"]["final_review_duration"], 25.0)

    def test_short_video_collection_keeps_natural_first_pass(self):
        video = self.root / "short.mp4"
        video.write_bytes(b"short-video")
        rows = [self.row(video, "select", start="00:00:00", end="00:00:50")]

        stats = self.builder.apply_selection_guardrails(
            rows,
            select_ceiling=0.10,
            review_ceiling=0.25,
            video_durations={str(video): 50.0},
            short_video_seconds=60,
        )

        self.assertEqual(rows[0]["decision"], "select")
        self.assertTrue(stats["video"]["short_collection_exception"])
        self.assertEqual(stats["video"]["final_select_duration"], 50.0)

    def test_unreadable_video_counts_only_when_it_was_not_already_excluded(self):
        readable = self.root / "readable.mp4"
        unreadable = self.root / "corrupt.mp4"
        readable.write_bytes(b"readable")
        unreadable.write_bytes(b"corrupt")
        rows = [
            self.row(readable, "select", start="00:00:00", end="00:00:30"),
            self.row(unreadable, "excluded"),
        ]

        stats = self.builder.apply_selection_guardrails(
            rows,
            select_ceiling=1.0,
            review_ceiling=1.0,
            video_durations={str(readable): 100.0},
            short_video_seconds=60,
        )

        self.assertEqual(stats["video"]["total_duration"], 100.0)
        self.assertEqual(rows[1]["decision"], "excluded")

        rows[1]["decision"] = "review"
        with self.assertRaisesRegex(ValueError, "missing readable duration"):
            self.builder.apply_selection_guardrails(
                rows,
                select_ceiling=1.0,
                review_ceiling=1.0,
                video_durations={str(readable): 100.0},
                short_video_seconds=60,
            )


if __name__ == "__main__":
    unittest.main()
