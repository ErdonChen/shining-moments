import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "validate_reference_calibration.py"
CATALOG_PATH = SKILL_DIR / "references" / "reference-source-map.json"
CATALOG_PAYLOAD = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
CATALOG = {source["id"]: source for source in CATALOG_PAYLOAD["sources"]}

PATTERN_DIMENSIONS = (
    "composition",
    "light",
    "color",
    "viewpoint",
    "subject_distance",
    "action_relationship",
    "camera_movement",
    "shot_duration",
    "pacing",
    "transition",
    "emotional_peak",
    "narrative_function",
    "opening_frame",
    "cover_frame",
)


class ValidateReferenceCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.log_path = self.root / "reference-calibration.json"

    def tearDown(self):
        self.tempdir.cleanup()

    def run_validator(self, payload):
        self.log_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(self.log_path)],
            check=False,
            capture_output=True,
            text=True,
        )

    def applicable_ids(self, access_mode):
        return {
            source_id
            for source_id, source in CATALOG.items()
            if source["access_mode"] == access_mode
            and set(source["media_kinds"]) & {"photo", "video"}
            and "vlog-event" in source["applicable_for"]
        }

    def default_automatic_ids(self):
        return {
            source_id
            for source_id in self.applicable_ids("automatic")
            if "vlog-event" in CATALOG[source_id].get("default_for", [])
        }

    def observed_source(self, source_id):
        source = CATALOG[source_id]
        media_kind = next(
            kind for kind in source["media_kinds"] if kind in {"photo", "video"}
        )
        record = {
            "source_id": source_id,
            "access_mode": source["access_mode"],
            "selection_status": "selected",
            "access_status": "accessed",
            "calibration_use": "used",
            "accessed_at": "2026-08-21T14:30:00+08:00",
            "search_terms": ["recent travel event visual reference"],
            "sample_scope": "Three actual public media samples visibly inspected",
            "discovery_mechanism": "Public search or visible curated surface",
            "access_limitations": "No material limitation in the inspected samples",
            "visible_samples": [
                {
                    "url": f"https://example.test/{source_id}/visible-sample",
                    "media_kind": media_kind,
                    "visibility": (
                        "full-image" if media_kind == "photo" else "video-playback"
                    ),
                    "observation": "A concrete visual pattern was visible in this sample",
                }
            ],
            "roles": source["roles"],
            "keywords": ["human-scale", "observational"],
            "patterns": {
                "composition": "The subject remains legible within its environment"
            },
        }
        if source["access_mode"] == "automatic":
            record["authentication_used"] = False
        else:
            record["user_visible_browser"] = True
        return record

    def failed_source(self, source_id):
        source = CATALOG[source_id]
        record = {
            "source_id": source_id,
            "access_mode": source["access_mode"],
            "selection_status": "selected",
            "access_status": "failed",
            "calibration_use": "skipped",
            "accessed_at": "2026-08-21T14:31:00+08:00",
            "search_terms": ["recent travel event visual reference"],
            "attempted_urls": [source["url"]],
            "access_limitations": "The page loaded without an inspectable media sample",
            "failure_reason": "Page-only or blocked-player evidence does not count",
            "visible_samples": [],
        }
        if source["access_mode"] == "automatic":
            record["authentication_used"] = False
        return record

    def skipped_source(self, source_id, reason="Not selected for this run"):
        return {
            "source_id": source_id,
            "access_mode": CATALOG[source_id]["access_mode"],
            "selection_status": "not-selected",
            "access_status": "not-accessed",
            "calibration_use": "skipped",
            "skip_reason": reason,
        }

    def summary(self, automatic_success, manual_success=None):
        manual_success = set(manual_success or [])
        automatic_success = set(automatic_success)
        editorial = next(
            source_id
            for source_id in sorted(automatic_success)
            if "editorial" in CATALOG[source_id]["roles"]
        )
        author = next(
            (
                source_id
                for source_id in sorted(automatic_success | manual_success)
                if "author-discovery" in CATALOG[source_id]["roles"]
            ),
            None,
        )
        trend = next(
            (
                source_id
                for source_id in sorted(manual_success)
                if "trend" in CATALOG[source_id]["roles"]
            ),
            None,
        )
        cross_sources = sorted(automatic_success)[:2]
        return {
            "long_term_standards": [
                {
                    "observation": "Visible editorial samples favor motivated framing",
                    "source_ids": [editorial],
                }
            ],
            "recent_platform_trends": (
                [
                    {
                        "observation": "A current manual sample opens on decisive action",
                        "source_ids": [trend],
                    }
                ]
                if trend
                else []
            ),
            "author_style_signals": (
                [
                    {
                        "observation": "One visible author sample uses close-follow movement",
                        "source_ids": [author],
                    }
                ]
                if author
                else []
            ),
            "cross_source_patterns": [
                {
                    "observation": "Human-scale detail connects place and emotion",
                    "source_ids": cross_sources,
                }
            ],
            "applied_selection_rules": [
                "Prefer intervals with a clear narrative and relationship beat"
            ],
            "pattern_dimensions": {
                dimension: f"Visible calibration for {dimension.replace('_', ' ')}"
                for dimension in PATTERN_DIMENSIONS
            },
            "popularity_use": "Discovery only; popularity is not a quality score",
            "calibration_state_note": "Automatic sources were ready; failures were recorded",
        }

    def live_payload(self):
        automatic_offered = self.applicable_ids("automatic")
        automatic_selected = self.default_automatic_ids()
        manual_offered = self.applicable_ids("manual-enhancement")
        sources = []
        for source_id in CATALOG:
            if source_id in automatic_selected:
                sources.append(self.observed_source(source_id))
            else:
                sources.append(self.skipped_source(source_id))
        return {
            "schema_version": 2,
            "material_type": "vlog-event",
            "media_kinds": ["photo", "video"],
            "automatic_selection": {
                "offered_source_ids": sorted(automatic_offered),
                "default_source_ids": sorted(automatic_selected),
                "selected_source_ids": sorted(automatic_selected),
                "selection_basis": "type-default",
            },
            "automatic_calibration": {
                "status": "ready",
                "checked_at": "2026-08-21T14:25:00+08:00",
                "successful_source_ids": sorted(automatic_selected),
                "failed_source_ids": [],
                "detail": "Selected automatic sources returned visible media",
            },
            "manual_enhancement": {
                "status": "declined",
                "offered_source_ids": sorted(manual_offered),
                "selected_source_ids": [],
                "user_readiness_confirmed": False,
                "detail": "The user declined optional manual enhancement",
            },
            "calibration_mode": "automatic",
            "static_fallback_authorized": False,
            "sources": sources,
            "calibration_summary": self.summary(automatic_selected),
        }

    def source_record(self, payload, source_id):
        return next(
            source for source in payload["sources"] if source["source_id"] == source_id
        )

    def set_automatic_selection(self, payload, selected, *, successful=None, failed=None):
        selected = set(selected)
        successful = set(selected if successful is None else successful)
        failed = set([] if failed is None else failed)
        self.assertEqual(selected, successful | failed)
        payload["automatic_selection"]["selected_source_ids"] = sorted(selected)
        payload["automatic_selection"]["selection_basis"] = "user-selected"
        for index, record in enumerate(payload["sources"]):
            source_id = record["source_id"]
            if CATALOG[source_id]["access_mode"] != "automatic":
                continue
            if source_id in successful:
                payload["sources"][index] = self.observed_source(source_id)
            elif source_id in failed:
                payload["sources"][index] = self.failed_source(source_id)
            else:
                payload["sources"][index] = self.skipped_source(source_id)
        status = "ready" if len(successful) >= 2 else "partial" if successful else "unavailable"
        payload["automatic_calibration"].update(
            {
                "status": status,
                "successful_source_ids": sorted(successful),
                "failed_source_ids": sorted(failed),
            }
        )
        payload["calibration_mode"] = "automatic" if status == "ready" else status
        if status == "ready":
            payload["calibration_summary"] = self.summary(successful)

    def complete_manual_enhancement(self, payload, source_id="youtube"):
        payload["manual_enhancement"].update(
            {
                "status": "completed",
                "selected_source_ids": [source_id],
                "user_readiness_confirmed": True,
                "detail": "The user completed login in a visible browser and confirmed readiness",
            }
        )
        index = next(
            index
            for index, record in enumerate(payload["sources"])
            if record["source_id"] == source_id
        )
        payload["sources"][index] = self.observed_source(source_id)
        if payload["automatic_calibration"]["status"] == "ready":
            payload["calibration_mode"] = "manual-enhanced"
            payload["calibration_summary"] = self.summary(
                payload["automatic_calibration"]["successful_source_ids"],
                {source_id},
            )

    def test_default_automatic_calibration_with_manual_declined_is_ready(self):
        result = self.run_validator(self.live_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

    def test_user_selected_automatic_subset_is_allowed(self):
        payload = self.live_payload()
        self.set_automatic_selection(payload, {"unsplash", "pexels-videos"})

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

    def test_absent_selection_must_use_type_specific_defaults(self):
        payload = self.live_payload()
        payload["automatic_selection"]["selected_source_ids"] = [
            "unsplash",
            "pexels-videos",
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("type-default", result.stderr)

    def test_manual_enhancement_requires_visible_content_and_user_browser(self):
        payload = self.live_payload()
        self.complete_manual_enhancement(payload)

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-manual-enhanced", result.stdout)

        self.source_record(payload, "youtube")["user_visible_browser"] = False
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 2)
        self.assertIn("visible browser", result.stderr)

    def test_manual_decline_never_blocks_ready_automatic_calibration(self):
        payload = self.live_payload()
        payload["manual_enhancement"]["detail"] = (
            "Manual enhancement was unavailable, so the automatic workflow continued"
        )

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

    def test_manual_failure_is_recorded_and_does_not_block_automatic_calibration(self):
        payload = self.live_payload()
        payload["manual_enhancement"].update(
            {
                "status": "cannot-use",
                "selected_source_ids": ["youtube"],
                "user_readiness_confirmed": True,
                "detail": "The visible player remained blocked after the user's own login attempt",
            }
        )
        index = next(
            index
            for index, record in enumerate(payload["sources"])
            if record["source_id"] == "youtube"
        )
        payload["sources"][index] = self.failed_source("youtube")

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

    def test_manual_evidence_cannot_replace_second_automatic_source(self):
        payload = self.live_payload()
        self.set_automatic_selection(payload, {"unsplash"})
        self.complete_manual_enhancement(payload)

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 3)
        self.assertIn("一个自动公开来源", result.stderr)

    def test_page_only_or_thumbnail_evidence_does_not_count(self):
        payload = self.live_payload()
        sample = self.source_record(payload, "unsplash")["visible_samples"][0]
        sample["visibility"] = "page-only"

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("do not count", result.stderr)

    def test_failed_automatic_source_is_skipped_and_recorded(self):
        payload = self.live_payload()
        selected = {"unsplash", "pexels-videos", "mixkit"}
        self.set_automatic_selection(
            payload,
            selected,
            successful={"unsplash", "pexels-videos"},
            failed={"mixkit"},
        )

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

        failed_record = self.source_record(payload, "mixkit")
        failed_record["visible_samples"] = [
            {
                "url": "https://example.test/page-only",
                "media_kind": "video",
                "visibility": "video-playback",
                "observation": "Invented",
            }
        ]
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 2)
        self.assertIn("empty visible_samples", result.stderr)

    def test_automatic_source_must_use_no_authentication(self):
        payload = self.live_payload()
        self.source_record(payload, "unsplash")["authentication_used"] = True

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("require no login", result.stderr)

    def test_partial_and_unavailable_states_pause_before_culling(self):
        partial = self.live_payload()
        self.set_automatic_selection(partial, {"unsplash"})
        result = self.run_validator(partial)
        self.assertEqual(result.returncode, 3)
        self.assertIn("两个来源", result.stderr)

        unavailable = self.live_payload()
        self.set_automatic_selection(
            unavailable,
            {"unsplash", "pexels-videos"},
            successful=set(),
            failed={"unsplash", "pexels-videos"},
        )
        result = self.run_validator(unavailable)
        self.assertEqual(result.returncode, 3)
        self.assertIn("当前无法查阅参考网站", result.stderr)

    def test_explicit_static_fallback_can_continue_from_partial(self):
        payload = self.live_payload()
        self.set_automatic_selection(payload, {"unsplash"})
        payload["calibration_mode"] = "static-authorized"
        payload["static_fallback_authorized"] = True
        payload["static_authorization"] = {
            "authorized_at": "2026-08-21T14:40:00+08:00",
            "user_confirmation": "同意记录限制并使用静态审美知识继续",
        }
        payload["calibration_summary"] = {
            "long_term_standards": [
                {"observation": "Static prior knowledge only", "source_ids": []}
            ],
            "recent_platform_trends": [],
            "author_style_signals": [],
            "cross_source_patterns": [],
            "applied_selection_rules": ["Use conservative static principles only"],
            "pattern_dimensions": {},
            "popularity_use": "No current popularity claims were made",
            "calibration_state_note": "Static fallback authorized after partial automatic evidence",
        }

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-static-authorized-partial", result.stdout)

    def test_authentication_secret_fields_are_rejected(self):
        for key in ("username", "password", "mfa_code", "cookies"):
            with self.subTest(key=key):
                payload = self.live_payload()
                payload["manual_enhancement"][key] = "must-not-be-handled"

                result = self.run_validator(payload)

                self.assertEqual(result.returncode, 2)
                self.assertIn("authentication-secret field", result.stderr)

    def test_every_catalog_source_must_have_an_evidence_or_skip_record(self):
        payload = self.live_payload()
        payload["sources"] = [
            record for record in payload["sources"] if record["source_id"] != "mixkit"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("mixkit", result.stderr)

    def test_summary_cannot_cite_failed_or_manual_unseen_sources(self):
        payload = self.live_payload()
        payload["calibration_summary"]["recent_platform_trends"] = [
            {
                "observation": "Unseen claimed trend",
                "source_ids": ["instagram"],
            }
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("unavailable sources", result.stderr)


if __name__ == "__main__":
    unittest.main()
