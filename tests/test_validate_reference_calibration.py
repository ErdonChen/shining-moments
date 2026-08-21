import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "validate_reference_calibration.py"

SOURCE_IDS = (
    "500px",
    "youtube",
    "shotdeck",
    "national-geographic-photography",
    "archdaily",
    "dezeen",
    "documentary-family-awards",
    "family-photojournalist-association",
    "lensculture",
    "magnum-photos",
    "this-is-reportage",
    "instagram",
    "vimeo-staff-picks",
    "nowness",
    "xiaohongshu",
    "x",
)

VLOG_REQUIRED = {
    "youtube",
    "shotdeck",
    "instagram",
    "vimeo-staff-picks",
    "nowness",
    "xiaohongshu",
    "x",
}

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

SOURCE_ROLES = {
    "500px": ["editorial", "author-discovery"],
    "youtube": ["trend", "author-discovery"],
    "shotdeck": ["editorial"],
    "national-geographic-photography": ["editorial"],
    "archdaily": ["editorial", "author-discovery"],
    "dezeen": ["editorial", "trend"],
    "documentary-family-awards": ["editorial", "author-discovery"],
    "family-photojournalist-association": ["editorial", "author-discovery"],
    "lensculture": ["editorial", "author-discovery"],
    "magnum-photos": ["editorial", "author-discovery"],
    "this-is-reportage": ["editorial", "author-discovery"],
    "instagram": ["trend", "author-discovery"],
    "vimeo-staff-picks": ["editorial", "author-discovery"],
    "nowness": ["editorial", "author-discovery"],
    "xiaohongshu": ["trend", "author-discovery"],
    "x": ["trend", "author-discovery"],
}


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

    def live_source(self, source_id):
        dimension = PATTERN_DIMENSIONS[SOURCE_IDS.index(source_id) % len(PATTERN_DIMENSIONS)]
        return {
            "source_id": source_id,
            "relevance": "relevant",
            "access_status": "accessed",
            "accessed_at": "2026-08-21T14:30:00+08:00",
            "search_terms": ["recent travel vlog staff picks cinematic rhythm"],
            "sample_scope": "Three public results or curated entries visible on the accessed page",
            "discovery_mechanism": "Public search, editorial selection, or visible trend surface",
            "access_limitations": "No material limitation observed in the public sample",
            "evidence_urls": [f"https://example.test/{source_id}/sample"],
            "roles": SOURCE_ROLES[source_id],
            "keywords": ["human-scale", "observational", "rhythmic"],
            "patterns": {
                dimension: "A concrete, source-observed pattern used for calibration"
            },
        }

    def skipped_source(self, source_id):
        return {
            "source_id": source_id,
            "relevance": "skipped",
            "access_status": "not-accessed",
            "skip_reason": "This source does not directly inform the active Vlog/event material type",
        }

    def live_payload(self):
        sources = [
            self.live_source(source_id)
            if source_id in VLOG_REQUIRED
            else self.skipped_source(source_id)
            for source_id in SOURCE_IDS
        ]
        return {
            "schema_version": 1,
            "material_type": "vlog-event",
            "connectivity_check": {
                "status": "reachable",
                "checked_at": "2026-08-21T14:25:00+08:00",
                "probe_targets": [
                    "https://vimeo.com/channels/staffpicks",
                    "https://www.youtube.com/",
                ],
                "detail": "Both public reference endpoints responded from the current environment",
            },
            "calibration_mode": "live",
            "static_fallback_authorized": False,
            "sources": sources,
            "calibration_summary": {
                "long_term_standards": [
                    {
                        "observation": "Editorial samples favor motivated shot changes",
                        "source_ids": ["vimeo-staff-picks", "nowness"],
                    }
                ],
                "recent_platform_trends": [
                    {
                        "observation": "Recent public posts foreground a decisive opening image",
                        "source_ids": ["xiaohongshu", "x", "instagram"],
                    }
                ],
                "author_style_signals": [
                    {
                        "observation": "One creator repeats handheld close-follow movement",
                        "source_ids": ["youtube"],
                    }
                ],
                "cross_source_patterns": [
                    {
                        "observation": "Human-scale details bridge place and emotion",
                        "source_ids": ["youtube", "nowness", "vimeo-staff-picks"],
                    }
                ],
                "applied_selection_rules": [
                    "Prefer intervals with a clear narrative function and emotional beat"
                ],
                "pattern_dimensions": {
                    dimension: f"Observed calibration for {dimension.replace('_', ' ')}"
                    for dimension in PATTERN_DIMENSIONS
                },
                "popularity_use": "Discovery only; likes and views are not quality scores",
            },
        }

    def static_authorized_payload(self):
        return {
            "schema_version": 1,
            "material_type": "vlog-event",
            "connectivity_check": {
                "status": "unavailable",
                "checked_at": "2026-08-21T14:25:00+08:00",
                "probe_targets": [
                    "https://vimeo.com/channels/staffpicks",
                    "https://www.youtube.com/",
                ],
                "detail": "Both reference-site checks failed from the current environment",
            },
            "calibration_mode": "static-authorized",
            "static_fallback_authorized": True,
            "static_authorization": {
                "authorized_at": "2026-08-21T14:28:00+08:00",
                "user_confirmation": "同意改用静态审美知识继续筛选",
            },
            "sources": [
                {
                    "source_id": source_id,
                    "relevance": "relevant" if source_id in VLOG_REQUIRED else "skipped",
                    "access_status": "not-accessed",
                    "access_limitations": "Network preflight failed before live reference research",
                    "skip_reason": (
                        "This source does not directly inform the active Vlog/event material type"
                        if source_id not in VLOG_REQUIRED
                        else ""
                    ),
                }
                for source_id in SOURCE_IDS
            ],
            "calibration_summary": {
                "long_term_standards": [
                    {
                        "observation": "Static prior knowledge only",
                        "source_ids": [],
                    }
                ],
                "recent_platform_trends": [],
                "author_style_signals": [],
                "cross_source_patterns": [],
                "applied_selection_rules": [
                    "Use only established static principles explicitly authorized by the user"
                ],
                "pattern_dimensions": {},
                "popularity_use": "No current popularity or trend claims were made",
            },
        }

    def test_live_calibration_is_ready_after_every_required_source_is_audited(self):
        result = self.run_validator(self.live_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-live", result.stdout)

    def test_unavailable_network_without_static_permission_pauses_before_culling(self):
        payload = self.static_authorized_payload()
        payload["calibration_mode"] = "paused"
        payload["static_fallback_authorized"] = False
        payload.pop("static_authorization")

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 3)
        self.assertIn(
            "当前无法查阅参考网站，因此不能获得实时参考/近期趋势",
            result.stderr,
        )
        self.assertIn("用户明确同意", result.stderr)

    def test_unavailable_network_with_explicit_static_permission_is_ready_static(self):
        result = self.run_validator(self.static_authorized_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-static-authorized", result.stdout)

    def test_connectivity_check_requires_two_public_reference_endpoints(self):
        payload = self.live_payload()
        payload["connectivity_check"]["probe_targets"] = [
            "https://vimeo.com/channels/staffpicks"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("at least two", result.stderr)

    def test_missing_required_live_source_is_rejected(self):
        payload = self.live_payload()
        payload["sources"] = [
            source for source in payload["sources"] if source["source_id"] != "nowness"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("nowness", result.stderr)

    def test_restricted_source_requires_limit_and_public_fallback_evidence(self):
        payload = self.live_payload()
        instagram = next(
            source for source in payload["sources"] if source["source_id"] == "instagram"
        )
        instagram["access_status"] = "restricted"
        instagram["access_limitations"] = "Login wall blocked individual post inspection"
        instagram["public_fallback_evidence_urls"] = [
            "https://www.instagram.com/explore/tags/travelvlog/"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready-live", result.stdout)

        instagram.pop("public_fallback_evidence_urls")
        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("public fallback evidence", result.stderr.lower())

    def test_unrelated_source_without_skip_reason_is_rejected(self):
        payload = self.live_payload()
        archdaily = next(
            source for source in payload["sources"] if source["source_id"] == "archdaily"
        )
        archdaily["skip_reason"] = ""

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("skip_reason", result.stderr)

    def test_static_mode_cannot_claim_live_access_or_recent_trends(self):
        payload = self.static_authorized_payload()
        payload["sources"][1]["access_status"] = "accessed"
        payload["calibration_summary"]["recent_platform_trends"] = [
            {"observation": "Invented current trend", "source_ids": ["youtube"]}
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("static-authorized", result.stderr)

    def test_static_mode_rejects_residual_live_evidence_fields(self):
        payload = self.static_authorized_payload()
        payload["sources"][1]["accessed_at"] = "2026-08-21T14:30:00+08:00"
        payload["sources"][1]["evidence_urls"] = [
            "https://www.youtube.com/watch?v=claimed-live"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("live evidence fields", result.stderr)

    def test_static_mode_still_accounts_for_required_sources_as_relevant(self):
        payload = self.static_authorized_payload()
        youtube = next(
            source for source in payload["sources"] if source["source_id"] == "youtube"
        )
        youtube["relevance"] = "skipped"
        youtube["skip_reason"] = "Deadline pressure"

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("required source youtube", result.stderr)

    def test_source_cannot_claim_a_role_outside_the_catalog(self):
        payload = self.live_payload()
        x_source = next(
            source for source in payload["sources"] if source["source_id"] == "x"
        )
        x_source["roles"] = ["editorial"]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("catalog roles", result.stderr)

    def test_summary_layers_must_cite_sources_with_matching_roles(self):
        payload = self.live_payload()
        payload["calibration_summary"]["long_term_standards"][0]["source_ids"] = [
            "x"
        ]

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("long_term_standards", result.stderr)
        self.assertIn("editorial", result.stderr)

    def test_live_summary_observation_must_cite_a_source(self):
        payload = self.live_payload()
        payload["calibration_summary"]["long_term_standards"][0]["source_ids"] = []

        result = self.run_validator(payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("source_ids", result.stderr)


if __name__ == "__main__":
    unittest.main()
