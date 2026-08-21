#!/usr/bin/env python3
"""Validate Shining Moments live-reference evidence before media culling."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PAUSE_NOTICE = (
    "当前无法查阅参考网站，因此不能获得实时参考/近期趋势。"
    "必须询问用户是否愿意改用已有的静态审美知识或固有印象继续；"
    "只有用户明确同意后才能继续，否则暂停筛选。"
)

MATERIAL_TYPES = {
    "mixed",
    "landscape-travel",
    "architecture-space",
    "documentary-culture",
    "portrait",
    "family",
    "friends",
    "vlog-event",
    "custom",
}

SOURCE_ROLES = {"editorial", "trend", "author-discovery"}

PATTERN_DIMENSIONS = {
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
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate live-reference research, access limitations, source accounting, "
            "and explicit static-fallback authorization before culling."
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "references"
        / "reference-source-map.json",
    )
    return parser.parse_args()


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value.strip()


def require_text_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    return [require_text(item, f"{label} item") for item in value]


def require_optional_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def require_timestamp(value: Any, label: str) -> str:
    timestamp = require_text(value, label)
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    return timestamp


def require_urls(value: Any, label: str) -> list[str]:
    urls = require_text_list(value, label)
    if any(not url.startswith(("https://", "http://")) for url in urls):
        raise ValueError(f"{label} must contain HTTP(S) URLs")
    return urls


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    try:
        return require_mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc


def load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path, "source catalog")
    if payload.get("schema_version") != 1:
        raise ValueError("source catalog schema_version must be 1")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source catalog sources must be a non-empty list")
    catalog: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(sources):
        source = require_mapping(value, f"source catalog item {index}")
        source_id = require_text(source.get("id"), f"source catalog item {index} id")
        if source_id in catalog:
            raise ValueError(f"source catalog contains duplicate id: {source_id}")
        catalog[source_id] = source
    return catalog


def required_source_ids(
    catalog: dict[str, dict[str, Any]], material_type: str
) -> set[str]:
    if material_type == "mixed":
        return set(catalog)
    return {
        source_id
        for source_id, source in catalog.items()
        if material_type in source.get("required_for", [])
    }


def validate_connectivity(payload: dict[str, Any]) -> str:
    check = require_mapping(payload.get("connectivity_check"), "connectivity_check")
    status = require_text(check.get("status"), "connectivity_check.status")
    if status not in {"reachable", "unavailable"}:
        raise ValueError("connectivity_check.status must be reachable or unavailable")
    require_timestamp(check.get("checked_at"), "connectivity_check.checked_at")
    probe_targets = require_urls(
        check.get("probe_targets"), "connectivity_check.probe_targets"
    )
    if len(set(probe_targets)) < 2:
        raise ValueError(
            "connectivity_check.probe_targets must contain at least two public reference endpoints"
        )
    require_text(check.get("detail"), "connectivity_check.detail")
    return status


def index_source_records(
    payload: dict[str, Any], catalog: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    values = payload.get("sources")
    if not isinstance(values, list):
        raise ValueError("sources must be a list")
    records: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        record = require_mapping(value, f"sources[{index}]")
        source_id = require_text(record.get("source_id"), f"sources[{index}].source_id")
        if source_id not in catalog:
            raise ValueError(f"unknown source_id: {source_id}")
        if source_id in records:
            raise ValueError(f"duplicate source record: {source_id}")
        records[source_id] = record
    missing = sorted(set(catalog) - set(records))
    if missing:
        raise ValueError("missing source records: " + ", ".join(missing))
    return records


def validate_observation_list(
    value: Any,
    label: str,
    known_source_ids: set[str],
    *,
    allow_empty: bool,
    cross_source: bool = False,
    require_sources: bool = False,
) -> list[dict[str, Any]]:
    values = require_optional_list(value, label)
    if not values and not allow_empty:
        raise ValueError(f"{label} must contain at least one observation")
    results: list[dict[str, Any]] = []
    for index, item in enumerate(values):
        observation = require_mapping(item, f"{label}[{index}]")
        require_text(observation.get("observation"), f"{label}[{index}].observation")
        source_ids = require_optional_list(
            observation.get("source_ids"), f"{label}[{index}].source_ids"
        )
        normalized = [
            require_text(source_id, f"{label}[{index}].source_ids item")
            for source_id in source_ids
        ]
        unknown = sorted(set(normalized) - known_source_ids)
        if unknown:
            raise ValueError(f"{label}[{index}] references unknown sources: {unknown}")
        if require_sources and not normalized:
            raise ValueError(f"{label}[{index}].source_ids must cite at least one source")
        if cross_source and len(set(normalized)) < 2:
            raise ValueError(f"{label}[{index}] must cite at least two sources")
        results.append(observation)
    return results


def validate_layer_roles(
    observations: list[dict[str, Any]],
    label: str,
    required_role: str,
    catalog: dict[str, dict[str, Any]],
) -> None:
    for index, observation in enumerate(observations):
        invalid = [
            source_id
            for source_id in observation["source_ids"]
            if required_role not in catalog[source_id].get("roles", [])
        ]
        if invalid:
            raise ValueError(
                f"{label}[{index}] must cite {required_role} sources; invalid: {invalid}"
            )


def validate_live_summary(
    summary: dict[str, Any],
    source_ids: set[str],
    catalog: dict[str, dict[str, Any]],
) -> None:
    long_term = validate_observation_list(
        summary.get("long_term_standards"),
        "calibration_summary.long_term_standards",
        source_ids,
        allow_empty=False,
        require_sources=True,
    )
    validate_layer_roles(
        long_term,
        "calibration_summary.long_term_standards",
        "editorial",
        catalog,
    )
    recent = validate_observation_list(
        summary.get("recent_platform_trends"),
        "calibration_summary.recent_platform_trends",
        source_ids,
        allow_empty=False,
        require_sources=True,
    )
    validate_layer_roles(
        recent,
        "calibration_summary.recent_platform_trends",
        "trend",
        catalog,
    )
    author = validate_observation_list(
        summary.get("author_style_signals"),
        "calibration_summary.author_style_signals",
        source_ids,
        allow_empty=False,
        require_sources=True,
    )
    validate_layer_roles(
        author,
        "calibration_summary.author_style_signals",
        "author-discovery",
        catalog,
    )
    validate_observation_list(
        summary.get("cross_source_patterns"),
        "calibration_summary.cross_source_patterns",
        source_ids,
        allow_empty=False,
        cross_source=True,
        require_sources=True,
    )
    require_text_list(
        summary.get("applied_selection_rules"),
        "calibration_summary.applied_selection_rules",
    )
    dimensions = require_mapping(
        summary.get("pattern_dimensions"), "calibration_summary.pattern_dimensions"
    )
    missing = sorted(PATTERN_DIMENSIONS - set(dimensions))
    if missing:
        raise ValueError("calibration summary is missing pattern dimensions: " + ", ".join(missing))
    for dimension in PATTERN_DIMENSIONS:
        require_text(
            dimensions.get(dimension),
            f"calibration_summary.pattern_dimensions.{dimension}",
        )
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")


def validate_live(
    payload: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    material_type: str,
) -> None:
    if payload.get("calibration_mode") != "live":
        raise ValueError("reachable connectivity requires calibration_mode live")
    if payload.get("static_fallback_authorized") is not False:
        raise ValueError("live mode must not claim static fallback authorization")

    records = index_source_records(payload, catalog)
    required = required_source_ids(catalog, material_type)
    if material_type == "custom" and not any(
        record.get("relevance") == "relevant" for record in records.values()
    ):
        raise ValueError("custom live calibration requires at least one relevant source")

    observed_roles: set[str] = set()
    relevant_ids: set[str] = set()
    for source_id, record in records.items():
        relevance = require_text(record.get("relevance"), f"{source_id}.relevance")
        if source_id in required and relevance != "relevant":
            raise ValueError(f"required source {source_id} cannot be skipped")
        if relevance == "skipped":
            require_text(record.get("skip_reason"), f"{source_id}.skip_reason")
            if record.get("access_status") != "not-accessed":
                raise ValueError(f"skipped source {source_id} must be not-accessed")
            continue
        if relevance != "relevant":
            raise ValueError(f"{source_id}.relevance must be relevant or skipped")

        relevant_ids.add(source_id)
        status = require_text(record.get("access_status"), f"{source_id}.access_status")
        if status not in {"accessed", "restricted"}:
            raise ValueError(f"relevant source {source_id} must be accessed or restricted")
        require_timestamp(record.get("accessed_at"), f"{source_id}.accessed_at")
        require_text_list(record.get("search_terms"), f"{source_id}.search_terms")
        require_text(record.get("sample_scope"), f"{source_id}.sample_scope")
        require_text(
            record.get("discovery_mechanism"), f"{source_id}.discovery_mechanism"
        )
        require_text(record.get("access_limitations"), f"{source_id}.access_limitations")
        require_urls(record.get("evidence_urls"), f"{source_id}.evidence_urls")
        if status == "restricted":
            try:
                require_urls(
                    record.get("public_fallback_evidence_urls"),
                    f"{source_id}.public fallback evidence",
                )
            except ValueError as exc:
                raise ValueError(
                    f"{source_id} restricted access requires public fallback evidence"
                ) from exc
        roles = set(require_text_list(record.get("roles"), f"{source_id}.roles"))
        unknown_roles = sorted(roles - SOURCE_ROLES)
        if unknown_roles:
            raise ValueError(f"{source_id} has unsupported roles: {unknown_roles}")
        catalog_roles = set(catalog[source_id].get("roles", []))
        unsupported_claims = sorted(roles - catalog_roles)
        if unsupported_claims:
            raise ValueError(
                f"{source_id} roles must match catalog roles; unsupported: "
                + ", ".join(unsupported_claims)
            )
        observed_roles.update(roles)
        require_text_list(record.get("keywords"), f"{source_id}.keywords")
        patterns = require_mapping(record.get("patterns"), f"{source_id}.patterns")
        if not patterns:
            raise ValueError(f"{source_id}.patterns must contain observed patterns")
        for dimension, observation in patterns.items():
            if dimension not in PATTERN_DIMENSIONS:
                raise ValueError(f"{source_id}.patterns has unknown dimension: {dimension}")
            require_text(observation, f"{source_id}.patterns.{dimension}")

    missing_roles = sorted(SOURCE_ROLES - observed_roles)
    if missing_roles:
        raise ValueError("live calibration must distinguish source roles: " + ", ".join(missing_roles))
    summary = require_mapping(payload.get("calibration_summary"), "calibration_summary")
    validate_live_summary(summary, relevant_ids, catalog)


def validate_static_authorized(
    payload: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    material_type: str,
) -> None:
    if payload.get("calibration_mode") != "static-authorized":
        raise ValueError("authorized static fallback requires calibration_mode static-authorized")
    if payload.get("static_fallback_authorized") is not True:
        raise ValueError("static-authorized mode requires explicit user authorization")
    authorization = require_mapping(
        payload.get("static_authorization"), "static_authorization"
    )
    require_timestamp(
        authorization.get("authorized_at"), "static_authorization.authorized_at"
    )
    require_text(
        authorization.get("user_confirmation"),
        "static_authorization.user_confirmation",
    )
    records = index_source_records(payload, catalog)
    required = required_source_ids(catalog, material_type)
    live_evidence_fields = {
        "accessed_at",
        "search_terms",
        "sample_scope",
        "discovery_mechanism",
        "evidence_urls",
        "public_fallback_evidence_urls",
        "roles",
        "keywords",
        "patterns",
    }
    for source_id, record in records.items():
        if record.get("access_status") != "not-accessed":
            raise ValueError(
                f"static-authorized mode cannot claim live access: {source_id}"
            )
        residual = sorted(
            field
            for field in live_evidence_fields
            if record.get(field) not in (None, "", [], {})
        )
        if residual:
            raise ValueError(
                f"static-authorized source {source_id} cannot retain live evidence fields: "
                + ", ".join(residual)
            )
        require_text(
            record.get("access_limitations"), f"{source_id}.access_limitations"
        )
        relevance = require_text(record.get("relevance"), f"{source_id}.relevance")
        if source_id in required and relevance != "relevant":
            raise ValueError(f"required source {source_id} cannot be skipped")
        if relevance == "skipped":
            require_text(record.get("skip_reason"), f"{source_id}.skip_reason")
        elif relevance != "relevant":
            raise ValueError(f"{source_id}.relevance must be relevant or skipped")

    summary = require_mapping(payload.get("calibration_summary"), "calibration_summary")
    validate_observation_list(
        summary.get("long_term_standards"),
        "calibration_summary.long_term_standards",
        set(catalog),
        allow_empty=False,
    )
    for field in (
        "recent_platform_trends",
        "author_style_signals",
        "cross_source_patterns",
    ):
        values = require_optional_list(summary.get(field), f"calibration_summary.{field}")
        if values:
            raise ValueError(
                f"static-authorized mode cannot claim live {field.replace('_', ' ')}"
            )
    require_text_list(
        summary.get("applied_selection_rules"),
        "calibration_summary.applied_selection_rules",
    )
    require_mapping(
        summary.get("pattern_dimensions"), "calibration_summary.pattern_dimensions"
    )
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")


def validate(payload: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> str:
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    material_type = require_text(payload.get("material_type"), "material_type")
    if material_type not in MATERIAL_TYPES:
        raise ValueError(f"unsupported material_type: {material_type}")
    status = validate_connectivity(payload)
    if status == "unavailable" and payload.get("static_fallback_authorized") is not True:
        if payload.get("calibration_mode") != "paused":
            raise ValueError("unavailable connectivity without authorization must pause")
        return "paused"
    if status == "unavailable":
        validate_static_authorized(payload, catalog, material_type)
        return "ready-static-authorized"
    validate_live(payload, catalog, material_type)
    return "ready-live"


def main() -> int:
    args = parse_args()
    try:
        payload = load_json(args.input, "calibration input")
        catalog = load_catalog(args.catalog)
        status = validate(payload, catalog)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if status == "paused":
        print(PAUSE_NOTICE, file=sys.stderr)
        return 3
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
