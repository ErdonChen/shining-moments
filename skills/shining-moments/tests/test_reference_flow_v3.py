import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_DIR / "references" / "reference-source-map.json"
VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_reference_calibration.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("reference_validator_v3", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReferenceFlowV3Tests(unittest.TestCase):
    def setUp(self):
        self.validator = load_validator()
        self.catalog_payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.catalog = {
            source["id"]: source for source in self.catalog_payload["sources"]
        }

    def observed(self, source_id, media_kinds):
        source = self.catalog[source_id]
        record = {
            "source_id": source_id,
            "access_mode": source["access_mode"],
            "selection_status": "selected",
            "access_status": "accessed",
            "calibration_use": "used",
            "accessed_at": "2026-08-22T12:00:00+08:00",
            "search_terms": ["family travel reference"],
            "sample_scope": "Visible samples inspected in the current run",
            "discovery_mechanism": "Public search or user-visible browser",
            "access_limitations": "No material limitation in the inspected samples",
            "visible_samples": [],
            "roles": source["roles"],
            "keywords": ["meaningful", "distinct"],
            "patterns": {"composition": "Clear subject and relationship context"},
        }
        for media_kind in media_kinds:
            sample = {
                "url": f"https://example.test/{source_id}/{media_kind}",
                "media_kind": media_kind,
                "visibility": (
                    "enlarged-preview"
                    if source_id == "google-images"
                    else "full-image"
                    if media_kind == "photo"
                    else "video-playback"
                ),
                "observation": "The visible sample supports a concrete visual judgment",
            }
            if source_id == "google-images":
                sample["origin_url"] = "https://origin.example/photo"
            record["visible_samples"].append(sample)
        if source["access_mode"] == "automatic":
            record["authentication_used"] = False
        else:
            record["user_visible_browser"] = True
        return record

    def skipped(self, source_id):
        return {
            "source_id": source_id,
            "access_mode": self.catalog[source_id]["access_mode"],
            "selection_status": "not-selected",
            "access_status": "not-accessed",
            "calibration_use": "skipped",
            "skip_reason": "Not selected for the optional manual enhancement",
        }

    def failed(self, source_id):
        source = self.catalog[source_id]
        record = {
            "source_id": source_id,
            "access_mode": source["access_mode"],
            "selection_status": "selected",
            "access_status": "failed",
            "calibration_use": "skipped",
            "accessed_at": "2026-08-22T12:01:00+08:00",
            "search_terms": ["family travel reference"],
            "attempted_urls": [source["url"]],
            "access_limitations": "No visible sample was available",
            "failure_reason": "The selected media could not be inspected",
            "visible_samples": [],
        }
        if source["access_mode"] == "automatic":
            record["authentication_used"] = False
        else:
            record["user_visible_browser"] = True
        return record

    def summary(self, source_ids):
        source_ids = sorted(source_ids)
        return {
            "long_term_standards": [
                {
                    "observation": "Visible samples favor meaningful, legible moments",
                    "source_ids": [source_ids[0]],
                }
            ],
            "recent_platform_trends": [],
            "author_style_signals": [],
            "cross_source_patterns": [
                {
                    "observation": "Distinct sources support the same visual rule",
                    "source_ids": source_ids[:2],
                }
            ],
            "applied_selection_rules": [
                "Prefer meaningful, high-quality, non-redundant material"
            ],
            "pattern_dimensions": {
                dimension: f"Visible evidence for {dimension}"
                for dimension in self.validator.PATTERN_DIMENSIONS
            },
            "popularity_use": "Discovery only",
            "calibration_state_note": "Photo and video gates were evaluated separately",
        }

    def ready_payload(self):
        automatic_media = {
            "photo": {
                "status": "ready",
                "successful_source_ids": [
                    "flickr-public",
                    "google-images",
                    "wikimedia-commons",
                ],
                "failed_source_ids": [],
                "detail": "Three automatic photo sources supplied visible samples",
            },
            "video": {
                "status": "ready",
                "successful_source_ids": ["google-videos", "wikimedia-commons"],
                "failed_source_ids": [],
                "detail": "Two automatic video sources supplied playable samples",
            },
        }
        observed_media = {
            "wikimedia-commons": ["photo", "video"],
            "flickr-public": ["photo"],
            "google-images": ["photo"],
            "google-videos": ["video"],
        }
        sources = [
            self.observed(source_id, observed_media[source_id])
            if source_id in observed_media
            else self.skipped(source_id)
            for source_id in self.catalog
        ]
        successful = set(observed_media)
        return {
            "schema_version": 3,
            "material_type": "vlog-event",
            "media_kinds": ["photo", "video"],
            "automatic_calibration": {
                "checked_at": "2026-08-22T12:00:00+08:00",
                "detail": "Every requested media kind was evaluated independently",
                "media": automatic_media,
            },
            "manual_enhancement": {
                "status": "declined",
                "mode": "none",
                "offered_source_ids": sorted(
                    source_id
                    for source_id, source in self.catalog.items()
                    if source["access_mode"] != "automatic"
                ),
                "selected_source_ids": [],
                "custom_sources": [],
                "user_readiness_confirmed": False,
                "detail": "The user declined optional manual enhancement",
            },
            "calibration_mode": "automatic",
            "static_fallback_authorized": False,
            "sources": sources,
            "calibration_summary": self.summary(successful),
        }

    def test_catalog_uses_only_the_approved_three_access_layers(self):
        self.assertEqual(self.catalog_payload["schema_version"], 3)
        pools = {}
        for source_id, source in self.catalog.items():
            pools.setdefault(source["access_mode"], set()).add(source_id)
        self.assertEqual(
            pools,
            {
                "automatic": {
                    "wikimedia-commons",
                    "flickr-public",
                    "google-images",
                    "google-videos",
                },
                "manual-challenge": {"unsplash", "pexels"},
                "manual-login": {
                    "xiaohongshu",
                    "instagram",
                    "youtube",
                    "bilibili",
                },
            },
        )

    def test_ready_payload_requires_two_visible_sources_for_each_media_kind(self):
        payload = self.ready_payload()

        result = self.validator.validate(payload, self.catalog)

        self.assertEqual(result, "ready-automatic")

        google_video = next(
            source for source in payload["sources"] if source["source_id"] == "google-videos"
        )
        payload["sources"][payload["sources"].index(google_video)] = self.failed(
            "google-videos"
        )
        payload["automatic_calibration"]["media"]["video"].update(
            {
                "status": "partial",
                "successful_source_ids": ["wikimedia-commons"],
                "failed_source_ids": ["google-videos"],
            }
        )
        payload["calibration_mode"] = "partial"

        result = self.validator.validate(payload, self.catalog)

        self.assertEqual(result, "paused-partial")

    def test_one_manual_challenge_source_can_complete_a_partial_video_gate(self):
        payload = self.ready_payload()
        payload["sources"] = [
            self.failed("google-videos")
            if source["source_id"] == "google-videos"
            else self.observed("pexels", ["video"])
            if source["source_id"] == "pexels"
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
        payload["manual_enhancement"].update(
            {
                "status": "completed",
                "mode": "challenge",
                "selected_source_ids": ["pexels"],
                "user_readiness_confirmed": True,
                "detail": "The user completed one Pexels challenge in a visible browser",
            }
        )
        payload["calibration_mode"] = "manual-enhanced"
        payload["calibration_summary"] = self.summary(
            {"wikimedia-commons", "flickr-public", "google-images", "pexels"}
        )

        result = self.validator.validate(payload, self.catalog)

        self.assertEqual(result, "ready-manual-enhanced")

    def test_google_images_requires_an_enlarged_preview_with_origin_url(self):
        payload = self.ready_payload()
        google = next(
            source for source in payload["sources"] if source["source_id"] == "google-images"
        )
        google["visible_samples"][0]["visibility"] = "thumbnail"
        google["visible_samples"][0].pop("origin_url")

        with self.assertRaisesRegex(ValueError, "enlarged-preview"):
            self.validator.validate(payload, self.catalog)


if __name__ == "__main__":
    unittest.main()
