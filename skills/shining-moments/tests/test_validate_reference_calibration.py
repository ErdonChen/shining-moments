import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import test_reference_flow_v3 as reference_fixture


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "validate_reference_calibration.py"
CATALOG_PATH = SKILL_DIR / "references" / "reference-source-map.json"


class ValidateReferenceCalibrationTests(unittest.TestCase):
    def setUp(self):
        fixture = reference_fixture.ReferenceFlowV3Tests(
            "test_ready_payload_requires_two_visible_sources_for_each_media_kind"
        )
        fixture.setUp()
        self.fixture = fixture
        self.validator = fixture.validator
        self.catalog = fixture.catalog

    def ready_payload(self):
        return copy.deepcopy(self.fixture.ready_payload())

    def run_validator(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "calibration.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(input_path),
                    "--catalog",
                    str(CATALOG_PATH),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

    def fail_google_video(self, payload):
        payload["sources"] = [
            self.fixture.failed("google-videos")
            if source["source_id"] == "google-videos"
            else source
            for source in payload["sources"]
        ]
        payload["automatic_calibration"]["media"]["video"].update(
            {
                "status": "partial",
                "successful_source_ids": ["wikimedia-commons"],
                "failed_source_ids": ["google-videos"],
            }
        )

    def test_ready_automatic_payload_passes_the_cli(self):
        result = self.run_validator(self.ready_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-automatic", result.stdout)

    def test_authentication_secret_fields_are_rejected_anywhere(self):
        for field in ("username", "password", "mfa_code", "cookies", "api_key"):
            with self.subTest(field=field):
                payload = self.ready_payload()
                payload["manual_enhancement"][field] = "must-not-be-handled"
                with self.assertRaisesRegex(ValueError, "authentication-secret"):
                    self.validator.validate(payload, self.catalog)

    def test_automatic_source_cannot_claim_authentication_or_challenge_use(self):
        payload = self.ready_payload()
        flickr = next(
            source
            for source in payload["sources"]
            if source["source_id"] == "flickr-public"
        )
        flickr["authentication_used"] = True

        with self.assertRaisesRegex(ValueError, "must require no authentication"):
            self.validator.validate(payload, self.catalog)

    def test_manual_challenge_requires_visible_evidence_in_user_browser(self):
        payload = self.ready_payload()
        payload["sources"] = [
            self.fixture.observed("pexels", ["photo"])
            if source["source_id"] == "pexels"
            else source
            for source in payload["sources"]
        ]
        pexels = next(
            source
            for source in payload["sources"]
            if source["source_id"] == "pexels"
        )
        pexels["user_visible_browser"] = False
        payload["manual_enhancement"].update(
            {
                "status": "completed",
                "mode": "challenge",
                "selected_source_ids": ["pexels"],
                "user_readiness_confirmed": True,
                "detail": "The user completed the visible challenge",
            }
        )
        payload["calibration_mode"] = "manual-enhanced"

        with self.assertRaisesRegex(ValueError, "visible browser"):
            self.validator.validate(payload, self.catalog)

    def test_failed_manual_attempt_does_not_block_ready_automatic_calibration(self):
        payload = self.ready_payload()
        payload["sources"] = [
            self.fixture.failed("unsplash")
            if source["source_id"] == "unsplash"
            else source
            for source in payload["sources"]
        ]
        payload["manual_enhancement"].update(
            {
                "status": "cannot-use",
                "mode": "challenge",
                "selected_source_ids": ["unsplash"],
                "user_readiness_confirmed": True,
                "detail": "The visible challenge did not yield usable samples",
            }
        )

        self.assertEqual(
            self.validator.validate(payload, self.catalog), "ready-automatic"
        )

    def test_thumbnail_or_page_only_photo_evidence_never_counts(self):
        payload = self.ready_payload()
        google = next(
            source
            for source in payload["sources"]
            if source["source_id"] == "google-images"
        )
        google["visible_samples"][0]["visibility"] = "thumbnail"

        with self.assertRaisesRegex(ValueError, "thumbnails do not count"):
            self.validator.validate(payload, self.catalog)

    def test_partial_media_gate_pauses_without_static_authorization(self):
        payload = self.ready_payload()
        self.fail_google_video(payload)
        payload["calibration_mode"] = "partial"

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 3)
        self.assertIn("paused-partial", result.stderr)

    def test_explicit_static_fallback_can_continue_from_partial_gate(self):
        payload = self.ready_payload()
        self.fail_google_video(payload)
        payload["calibration_mode"] = "static-authorized"
        payload["static_fallback_authorized"] = True
        payload["static_authorization"] = {
            "authorized_at": "2026-08-22T13:00:00+08:00",
            "user_confirmation": "Continue with static standards despite the partial video gate",
        }
        payload["calibration_summary"].update(
            {
                "recent_platform_trends": [],
                "author_style_signals": [],
                "cross_source_patterns": [],
            }
        )

        self.assertEqual(
            self.validator.validate(payload, self.catalog),
            "ready-static-authorized-partial",
        )

    def test_every_catalog_source_requires_an_evidence_or_skip_record(self):
        payload = self.ready_payload()
        payload["sources"] = [
            source
            for source in payload["sources"]
            if source["source_id"] != "instagram"
        ]

        with self.assertRaisesRegex(ValueError, "missing source records: instagram"):
            self.validator.validate(payload, self.catalog)

    def test_ready_summary_cannot_cite_an_unseen_manual_source(self):
        payload = self.ready_payload()
        payload["calibration_summary"]["author_style_signals"] = [
            {
                "observation": "An unsupported live style claim",
                "source_ids": ["instagram"],
            }
        ]

        with self.assertRaisesRegex(ValueError, "unavailable sources"):
            self.validator.validate(payload, self.catalog)

    def test_custom_url_can_be_the_single_manual_enhancement(self):
        payload = self.ready_payload()
        custom = {
            "id": "custom-example",
            "name": "User supplied reference",
            "url": "https://example.org/reference",
            "access_mode": "manual-custom",
            "media_kinds": ["photo"],
            "roles": ["editorial", "author-discovery"],
        }
        payload["manual_enhancement"].update(
            {
                "status": "completed",
                "mode": "custom",
                "selected_source_ids": ["custom-example"],
                "custom_sources": [custom],
                "user_readiness_confirmed": True,
                "detail": "The custom public page was visible in the user browser",
            }
        )
        custom_record = {
            "source_id": "custom-example",
            "access_mode": "manual-custom",
            "selection_status": "selected",
            "access_status": "accessed",
            "calibration_use": "used",
            "accessed_at": "2026-08-22T13:15:00+08:00",
            "search_terms": ["user supplied reference"],
            "sample_scope": "Visible samples inspected in the current run",
            "discovery_mechanism": "User supplied URL",
            "access_limitations": "No material limitation in the inspected sample",
            "visible_samples": [
                {
                    "url": "https://example.org/reference/photo",
                    "media_kind": "photo",
                    "visibility": "full-image",
                    "observation": "A visible full image supports a concrete judgment",
                }
            ],
            "roles": ["editorial", "author-discovery"],
            "keywords": ["custom"],
            "patterns": {"composition": "Clear subject hierarchy"},
            "user_visible_browser": True,
        }
        payload["sources"].append(custom_record)
        payload["calibration_mode"] = "manual-enhanced"

        self.assertEqual(
            self.validator.validate(payload, self.catalog),
            "ready-manual-enhanced",
        )


if __name__ == "__main__":
    unittest.main()
