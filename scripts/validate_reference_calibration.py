#!/usr/bin/env python3
"""Validate Shining Moments reference evidence before personal-media culling."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


UNAVAILABLE_NOTICE = (
    "当前无法查阅参考网站，因此不能获得实时参考/近期趋势。"
    "必须询问用户是否愿意改用已有的静态审美知识或固有印象继续；"
    "只有用户明确同意后才能继续，否则暂停筛选。"
)
PARTIAL_NOTICE = (
    "当前仅有一个自动公开来源返回了实际可见样本，未达到至少两个来源的自动视觉校准门槛。"
    "必须询问用户是否愿意在明确记录此限制后改用静态审美知识继续；"
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
MEDIA_KINDS = {"photo", "video"}
SOURCE_ROLES = {"editorial", "trend", "author-discovery"}
ACCESS_MODES = {"automatic", "manual-enhancement"}
AUTOMATIC_STATES = {"ready", "partial", "unavailable"}
MANUAL_STATES = {"completed", "declined", "cannot-use"}
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
SENSITIVE_KEY_PARTS = {
    "credential",
    "credentials",
    "cookie",
    "cookies",
    "mfa",
    "otp",
    "passwd",
    "password",
    "secret",
    "secrets",
    "token",
    "tokens",
    "username",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate automatic public-reference samples, optional user-managed "
            "manual enhancement, per-source limitations, and fallback readiness."
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


def require_text_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise ValueError(f"{label} must be {qualifier}")
    return [require_text(item, f"{label} item") for item in value]


def require_timestamp(value: Any, label: str) -> str:
    timestamp = require_text(value, label)
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    return timestamp


def require_urls(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    urls = require_text_list(value, label, allow_empty=allow_empty)
    if any(not url.startswith(("https://", "http://")) for url in urls):
        raise ValueError(f"{label} must contain HTTP(S) URLs")
    return urls


def require_exact_id_set(value: Any, expected: set[str], label: str) -> set[str]:
    actual_list = require_text_list(value, label, allow_empty=True)
    if len(actual_list) != len(set(actual_list)):
        raise ValueError(f"{label} must not contain duplicates")
    actual = set(actual_list)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{label} does not match routed sources; missing={missing}, extra={extra}")
    return actual


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    try:
        return require_mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc


def reject_sensitive_fields(value: Any, label: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            parts = set(normalized.split("_"))
            if parts & SENSITIVE_KEY_PARTS:
                raise ValueError(
                    f"{label} contains prohibited authentication-secret field: {key}"
                )
            reject_sensitive_fields(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive_fields(child, f"{label}[{index}]")


def load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path, "source catalog")
    if payload.get("schema_version") != 2:
        raise ValueError("source catalog schema_version must be 2")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source catalog sources must be a non-empty list")
    catalog: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(sources):
        source = require_mapping(value, f"source catalog item {index}")
        source_id = require_text(source.get("id"), f"source catalog item {index} id")
        if source_id == "x" or source.get("name") == "X":
            raise ValueError("X must not appear in the source catalog")
        if source_id in catalog:
            raise ValueError(f"source catalog contains duplicate id: {source_id}")
        require_text(source.get("name"), f"source catalog item {index} name")
        require_urls([source.get("url")], f"source catalog item {index} url")
        access_mode = require_text(
            source.get("access_mode"), f"source catalog item {index} access_mode"
        )
        if access_mode not in ACCESS_MODES:
            raise ValueError(f"unsupported source access_mode: {access_mode}")
        media_kinds = set(
            require_text_list(
                source.get("media_kinds"), f"source catalog item {index} media_kinds"
            )
        )
        if media_kinds - MEDIA_KINDS:
            raise ValueError(f"unsupported source media kinds: {sorted(media_kinds - MEDIA_KINDS)}")
        roles = set(
            require_text_list(source.get("roles"), f"source catalog item {index} roles")
        )
        if roles - SOURCE_ROLES:
            raise ValueError(f"unsupported source roles: {sorted(roles - SOURCE_ROLES)}")
        applicable = set(
            require_text_list(
                source.get("applicable_for"),
                f"source catalog item {index} applicable_for",
            )
        )
        if applicable - (MATERIAL_TYPES - {"mixed", "custom"}):
            raise ValueError(f"unsupported applicable material types: {sorted(applicable)}")
        defaults = set(
            require_text_list(
                source.get("default_for", []),
                f"source catalog item {index} default_for",
                allow_empty=True,
            )
        )
        if defaults - applicable:
            raise ValueError(f"{source_id} default_for must be a subset of applicable_for")
        if access_mode == "manual-enhancement" and defaults:
            raise ValueError(f"manual source {source_id} cannot be an automatic default")
        catalog[source_id] = source
    return catalog


def routed_source_ids(
    catalog: dict[str, dict[str, Any]],
    material_type: str,
    media_kinds: set[str],
    access_mode: str,
) -> set[str]:
    routed: set[str] = set()
    for source_id, source in catalog.items():
        if source.get("access_mode") != access_mode:
            continue
        if not (set(source.get("media_kinds", [])) & media_kinds):
            continue
        if material_type in {"mixed", "custom"} or material_type in source.get(
            "applicable_for", []
        ):
            routed.add(source_id)
    return routed


def default_automatic_source_ids(
    catalog: dict[str, dict[str, Any]],
    material_type: str,
    media_kinds: set[str],
) -> set[str]:
    applicable = routed_source_ids(catalog, material_type, media_kinds, "automatic")
    if material_type in {"mixed", "custom"}:
        return applicable
    return {
        source_id
        for source_id in applicable
        if material_type in catalog[source_id].get("default_for", [])
    }


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


def validate_visible_samples(
    record: dict[str, Any],
    source_id: str,
    catalog_source: dict[str, Any],
    media_kinds: set[str],
) -> None:
    samples = record.get("visible_samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError(
            f"{source_id}.visible_samples must contain actual visible image/video samples"
        )
    allowed_kinds = set(catalog_source.get("media_kinds", [])) & media_kinds
    for index, value in enumerate(samples):
        sample = require_mapping(value, f"{source_id}.visible_samples[{index}]")
        require_urls([sample.get("url")], f"{source_id}.visible_samples[{index}].url")
        media_kind = require_text(
            sample.get("media_kind"), f"{source_id}.visible_samples[{index}].media_kind"
        )
        if media_kind not in allowed_kinds:
            raise ValueError(f"{source_id} visible sample has unsuitable media_kind: {media_kind}")
        expected_visibility = "full-image" if media_kind == "photo" else "video-playback"
        if sample.get("visibility") != expected_visibility:
            raise ValueError(
                f"{source_id} {media_kind} sample visibility must be {expected_visibility}; "
                "page-only, text-only, thumbnails, and search snippets do not count"
            )
        require_text(
            sample.get("observation"), f"{source_id}.visible_samples[{index}].observation"
        )


def validate_observed_source(
    record: dict[str, Any],
    source_id: str,
    catalog_source: dict[str, Any],
    media_kinds: set[str],
) -> None:
    if record.get("calibration_use") != "used":
        raise ValueError(f"accessed source {source_id} must set calibration_use used")
    require_timestamp(record.get("accessed_at"), f"{source_id}.accessed_at")
    require_text_list(record.get("search_terms"), f"{source_id}.search_terms")
    require_text(record.get("sample_scope"), f"{source_id}.sample_scope")
    require_text(record.get("discovery_mechanism"), f"{source_id}.discovery_mechanism")
    require_text(record.get("access_limitations"), f"{source_id}.access_limitations")
    validate_visible_samples(record, source_id, catalog_source, media_kinds)
    roles = set(require_text_list(record.get("roles"), f"{source_id}.roles"))
    unsupported = roles - set(catalog_source.get("roles", []))
    if unsupported:
        raise ValueError(f"{source_id} roles must match catalog roles; unsupported: {sorted(unsupported)}")
    require_text_list(record.get("keywords"), f"{source_id}.keywords")
    patterns = require_mapping(record.get("patterns"), f"{source_id}.patterns")
    if not patterns:
        raise ValueError(f"{source_id}.patterns must contain observed patterns")
    for dimension, observation in patterns.items():
        if dimension not in PATTERN_DIMENSIONS:
            raise ValueError(f"{source_id}.patterns has unknown dimension: {dimension}")
        require_text(observation, f"{source_id}.patterns.{dimension}")


def validate_failed_source(record: dict[str, Any], source_id: str) -> None:
    if record.get("calibration_use") != "skipped":
        raise ValueError(f"failed source {source_id} must set calibration_use skipped")
    require_timestamp(record.get("accessed_at"), f"{source_id}.accessed_at")
    require_text_list(record.get("search_terms"), f"{source_id}.search_terms")
    require_urls(record.get("attempted_urls"), f"{source_id}.attempted_urls")
    require_text(record.get("access_limitations"), f"{source_id}.access_limitations")
    require_text(record.get("failure_reason"), f"{source_id}.failure_reason")
    samples = record.get("visible_samples")
    if samples != []:
        raise ValueError(f"failed source {source_id} must have an empty visible_samples list")


def validate_source_records(
    records: dict[str, dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
    media_kinds: set[str],
    automatic_selected: set[str],
    manual_selected: set[str],
) -> tuple[set[str], set[str], set[str], set[str]]:
    automatic_success: set[str] = set()
    automatic_failed: set[str] = set()
    manual_success: set[str] = set()
    manual_failed: set[str] = set()
    for source_id, record in records.items():
        source = catalog[source_id]
        access_mode = source["access_mode"]
        if record.get("access_mode") != access_mode:
            raise ValueError(f"{source_id}.access_mode must match the catalog")
        selected = source_id in (
            automatic_selected if access_mode == "automatic" else manual_selected
        )
        if not selected:
            if record.get("selection_status") != "not-selected":
                raise ValueError(f"unselected source {source_id} must be not-selected")
            if record.get("access_status") != "not-accessed":
                raise ValueError(f"unselected source {source_id} must be not-accessed")
            if record.get("calibration_use") != "skipped":
                raise ValueError(f"unselected source {source_id} must be skipped")
            require_text(record.get("skip_reason"), f"{source_id}.skip_reason")
            continue
        if record.get("selection_status") != "selected":
            raise ValueError(f"selected source {source_id} must set selection_status selected")
        status = require_text(record.get("access_status"), f"{source_id}.access_status")
        if status == "accessed":
            validate_observed_source(record, source_id, source, media_kinds)
            if access_mode == "automatic":
                if record.get("authentication_used") is not False:
                    raise ValueError(f"automatic source {source_id} must require no login")
                automatic_success.add(source_id)
            else:
                if record.get("user_visible_browser") is not True:
                    raise ValueError(
                        f"manual source {source_id} must be observed in the user's visible browser"
                    )
                manual_success.add(source_id)
        elif status == "failed":
            validate_failed_source(record, source_id)
            if access_mode == "automatic":
                if record.get("authentication_used") is not False:
                    raise ValueError(f"automatic source {source_id} must not use authentication")
                automatic_failed.add(source_id)
            else:
                manual_failed.add(source_id)
        else:
            raise ValueError(f"selected source {source_id} must be accessed or failed")
    return automatic_success, automatic_failed, manual_success, manual_failed


def validate_observation_list(
    value: Any,
    label: str,
    allowed_source_ids: set[str],
    *,
    allow_empty: bool,
    cross_source: bool = False,
    required_role: str | None = None,
    catalog: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f"{label} must be {'a list' if allow_empty else 'a non-empty list'}")
    results: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        observation = require_mapping(item, f"{label}[{index}]")
        require_text(observation.get("observation"), f"{label}[{index}].observation")
        source_ids = set(
            require_text_list(
                observation.get("source_ids"),
                f"{label}[{index}].source_ids",
                allow_empty=True,
            )
        )
        unknown = sorted(source_ids - allowed_source_ids)
        if unknown:
            raise ValueError(f"{label}[{index}] cites unavailable sources: {unknown}")
        if not source_ids:
            raise ValueError(f"{label}[{index}].source_ids must cite visible evidence")
        if cross_source and len(source_ids) < 2:
            raise ValueError(f"{label}[{index}] must cite at least two automatic sources")
        if required_role and catalog:
            invalid = sorted(
                source_id
                for source_id in source_ids
                if required_role not in catalog[source_id].get("roles", [])
            )
            if invalid:
                raise ValueError(f"{label}[{index}] must cite {required_role} sources; invalid: {invalid}")
        results.append(observation)
    return results


def validate_ready_summary(
    payload: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    automatic_success: set[str],
    manual_success: set[str],
) -> None:
    summary = require_mapping(payload.get("calibration_summary"), "calibration_summary")
    validate_observation_list(
        summary.get("long_term_standards"),
        "calibration_summary.long_term_standards",
        automatic_success,
        allow_empty=False,
        required_role="editorial",
        catalog=catalog,
    )
    validate_observation_list(
        summary.get("recent_platform_trends"),
        "calibration_summary.recent_platform_trends",
        manual_success,
        allow_empty=True,
        required_role="trend",
        catalog=catalog,
    )
    validate_observation_list(
        summary.get("author_style_signals"),
        "calibration_summary.author_style_signals",
        automatic_success | manual_success,
        allow_empty=True,
        required_role="author-discovery",
        catalog=catalog,
    )
    validate_observation_list(
        summary.get("cross_source_patterns"),
        "calibration_summary.cross_source_patterns",
        automatic_success,
        allow_empty=False,
        cross_source=True,
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
        require_text(dimensions.get(dimension), f"calibration_summary.pattern_dimensions.{dimension}")
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")
    require_text(summary.get("calibration_state_note"), "calibration_summary.calibration_state_note")


def validate_static_summary(payload: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> None:
    authorization = require_mapping(payload.get("static_authorization"), "static_authorization")
    require_timestamp(authorization.get("authorized_at"), "static_authorization.authorized_at")
    require_text(authorization.get("user_confirmation"), "static_authorization.user_confirmation")
    summary = require_mapping(payload.get("calibration_summary"), "calibration_summary")
    long_term = summary.get("long_term_standards")
    if not isinstance(long_term, list) or not long_term:
        raise ValueError("static calibration requires long_term_standards")
    for index, item in enumerate(long_term):
        observation = require_mapping(item, f"calibration_summary.long_term_standards[{index}]")
        require_text(observation.get("observation"), f"long_term_standards[{index}].observation")
        require_text_list(
            observation.get("source_ids", []),
            f"long_term_standards[{index}].source_ids",
            allow_empty=True,
        )
    for field in ("recent_platform_trends", "author_style_signals", "cross_source_patterns"):
        if summary.get(field) != []:
            raise ValueError(f"static-authorized mode cannot claim live {field.replace('_', ' ')}")
    require_text_list(summary.get("applied_selection_rules"), "calibration_summary.applied_selection_rules")
    require_mapping(summary.get("pattern_dimensions"), "calibration_summary.pattern_dimensions")
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")
    require_text(summary.get("calibration_state_note"), "calibration_summary.calibration_state_note")


def validate(payload: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> str:
    reject_sensitive_fields(payload)
    if payload.get("schema_version") != 2:
        raise ValueError("schema_version must be 2")
    material_type = require_text(payload.get("material_type"), "material_type")
    if material_type not in MATERIAL_TYPES:
        raise ValueError(f"unsupported material_type: {material_type}")
    media_kind_list = require_text_list(payload.get("media_kinds"), "media_kinds")
    media_kinds = set(media_kind_list)
    if len(media_kind_list) != len(media_kinds) or media_kinds - MEDIA_KINDS:
        raise ValueError("media_kinds must contain unique photo/video values")

    automatic_applicable = routed_source_ids(catalog, material_type, media_kinds, "automatic")
    manual_applicable = routed_source_ids(
        catalog, material_type, media_kinds, "manual-enhancement"
    )
    automatic_defaults = default_automatic_source_ids(catalog, material_type, media_kinds)

    selection = require_mapping(payload.get("automatic_selection"), "automatic_selection")
    require_exact_id_set(
        selection.get("offered_source_ids"), automatic_applicable, "automatic_selection.offered_source_ids"
    )
    require_exact_id_set(
        selection.get("default_source_ids"), automatic_defaults, "automatic_selection.default_source_ids"
    )
    automatic_selected_list = require_text_list(
        selection.get("selected_source_ids"), "automatic_selection.selected_source_ids"
    )
    automatic_selected = set(automatic_selected_list)
    if len(automatic_selected_list) != len(automatic_selected):
        raise ValueError("automatic_selection.selected_source_ids must not contain duplicates")
    if automatic_selected - automatic_applicable:
        raise ValueError("automatic selection contains sources not applicable to this material")
    basis = require_text(selection.get("selection_basis"), "automatic_selection.selection_basis")
    if basis == "type-default" and automatic_selected != automatic_defaults:
        raise ValueError("type-default selection must use the type-specific default sources")
    if basis == "custom-brief" and material_type != "custom":
        raise ValueError("custom-brief selection is only valid for custom material")
    if basis not in {"type-default", "user-selected", "custom-brief"}:
        raise ValueError("unsupported automatic selection_basis")

    manual = require_mapping(payload.get("manual_enhancement"), "manual_enhancement")
    require_exact_id_set(
        manual.get("offered_source_ids"), manual_applicable, "manual_enhancement.offered_source_ids"
    )
    manual_selected_list = require_text_list(
        manual.get("selected_source_ids"),
        "manual_enhancement.selected_source_ids",
        allow_empty=True,
    )
    manual_selected = set(manual_selected_list)
    if len(manual_selected_list) != len(manual_selected):
        raise ValueError("manual_enhancement.selected_source_ids must not contain duplicates")
    if manual_selected - manual_applicable:
        raise ValueError("manual enhancement contains inapplicable or prohibited sources")
    manual_status = require_text(manual.get("status"), "manual_enhancement.status")
    if manual_status not in MANUAL_STATES:
        raise ValueError(f"unsupported manual enhancement status: {manual_status}")
    require_text(manual.get("detail"), "manual_enhancement.detail")
    readiness = manual.get("user_readiness_confirmed")
    if manual_status == "declined" and (manual_selected or readiness is not False):
        raise ValueError("declined manual enhancement must select no sources and not claim readiness")
    if manual_status == "completed" and (not manual_selected or readiness is not True):
        raise ValueError("completed manual enhancement requires readiness and selected sources")

    records = index_source_records(payload, catalog)
    automatic_success, automatic_failed, manual_success, manual_failed = validate_source_records(
        records,
        catalog,
        media_kinds,
        automatic_selected,
        manual_selected,
    )
    if manual_status == "completed" and not manual_success:
        raise ValueError("manual-enhanced calibration requires actually visible manual content")
    if manual_status == "cannot-use" and manual_success:
        raise ValueError("cannot-use manual enhancement cannot contain successful manual samples")

    automatic = require_mapping(payload.get("automatic_calibration"), "automatic_calibration")
    require_timestamp(automatic.get("checked_at"), "automatic_calibration.checked_at")
    require_text(automatic.get("detail"), "automatic_calibration.detail")
    require_exact_id_set(
        automatic.get("successful_source_ids"),
        automatic_success,
        "automatic_calibration.successful_source_ids",
    )
    require_exact_id_set(
        automatic.get("failed_source_ids"),
        automatic_failed,
        "automatic_calibration.failed_source_ids",
    )
    computed_state = "ready" if len(automatic_success) >= 2 else "partial" if automatic_success else "unavailable"
    state = require_text(automatic.get("status"), "automatic_calibration.status")
    if state not in AUTOMATIC_STATES or state != computed_state:
        raise ValueError(f"automatic_calibration.status must be {computed_state} from visible samples")

    calibration_mode = require_text(payload.get("calibration_mode"), "calibration_mode")
    static_authorized = payload.get("static_fallback_authorized")
    if state != "ready":
        expected_mode = state
        if static_authorized is True:
            if calibration_mode != "static-authorized":
                raise ValueError("authorized fallback requires calibration_mode static-authorized")
            validate_static_summary(payload, catalog)
            return f"ready-static-authorized-{state}"
        if static_authorized is not False or calibration_mode != expected_mode:
            raise ValueError(f"automatic {state} state must remain {expected_mode} until authorization")
        return f"paused-{state}"

    if static_authorized is not False:
        raise ValueError("ready automatic calibration must not claim static fallback authorization")
    expected_mode = "manual-enhanced" if manual_status == "completed" else "automatic"
    if calibration_mode != expected_mode:
        raise ValueError(f"ready calibration_mode must be {expected_mode}")
    validate_ready_summary(payload, catalog, automatic_success, manual_success)
    return f"ready-{expected_mode}"


def main() -> int:
    args = parse_args()
    try:
        payload = load_json(args.input, "calibration input")
        catalog = load_catalog(args.catalog)
        status = validate(payload, catalog)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if status == "paused-partial":
        print(PARTIAL_NOTICE, file=sys.stderr)
        return 3
    if status == "paused-unavailable":
        print(UNAVAILABLE_NOTICE, file=sys.stderr)
        return 3
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
