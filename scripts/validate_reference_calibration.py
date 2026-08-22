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
    "当前至少一种素材类型只有一个实际可见参考来源，未达到两个独立来源的视觉校准门槛。"
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
CATALOG_ACCESS_MODES = {"automatic", "manual-challenge", "manual-login"}
ACCESS_MODES = CATALOG_ACCESS_MODES | {"manual-custom"}
MANUAL_MODES = {"none", "challenge", "login", "custom"}
MANUAL_STATES = {"completed", "declined", "cannot-use"}
AUTOMATIC_STATES = {"ready", "partial", "unavailable"}
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
    "api",
    "credential",
    "credentials",
    "cookie",
    "cookies",
    "key",
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
            "Validate fixed automatic reference sources, optional user-managed "
            "challenge/login/custom enhancement, and per-media readiness."
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


def require_text_list(
    value: Any, label: str, *, allow_empty: bool = False
) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise ValueError(f"{label} must be {qualifier}")
    result = [require_text(item, f"{label} item") for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def require_timestamp(value: Any, label: str) -> str:
    timestamp = require_text(value, label)
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    return timestamp


def require_urls(
    value: Any, label: str, *, allow_empty: bool = False
) -> list[str]:
    urls = require_text_list(value, label, allow_empty=allow_empty)
    if any(not url.startswith(("https://", "http://")) for url in urls):
        raise ValueError(f"{label} must contain HTTP(S) URLs")
    return urls


def require_exact_id_set(value: Any, expected: set[str], label: str) -> set[str]:
    actual = set(require_text_list(value, label, allow_empty=True))
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"{label} does not match routed sources; missing={missing}, extra={extra}"
        )
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
            if set(normalized.split("_")) & SENSITIVE_KEY_PARTS:
                raise ValueError(
                    f"{label} contains prohibited authentication-secret field: {key}"
                )
            reject_sensitive_fields(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive_fields(child, f"{label}[{index}]")


def validate_source_definition(
    source: dict[str, Any], label: str, *, custom: bool = False
) -> dict[str, Any]:
    source_id = require_text(source.get("id"), f"{label}.id")
    require_text(source.get("name"), f"{label}.name")
    require_urls([source.get("url")], f"{label}.url")
    access_mode = require_text(source.get("access_mode"), f"{label}.access_mode")
    allowed_modes = {"manual-custom"} if custom else CATALOG_ACCESS_MODES
    if access_mode not in allowed_modes:
        raise ValueError(f"unsupported source access_mode: {access_mode}")
    media_kinds = set(require_text_list(source.get("media_kinds"), f"{label}.media_kinds"))
    if media_kinds - MEDIA_KINDS:
        raise ValueError(f"unsupported source media kinds: {sorted(media_kinds - MEDIA_KINDS)}")
    roles = set(require_text_list(source.get("roles"), f"{label}.roles"))
    if roles - SOURCE_ROLES:
        raise ValueError(f"unsupported source roles: {sorted(roles - SOURCE_ROLES)}")
    if not custom:
        applicable = set(
            require_text_list(source.get("applicable_for"), f"{label}.applicable_for")
        )
        if applicable - (MATERIAL_TYPES - {"mixed", "custom"}):
            raise ValueError(
                f"unsupported applicable material types: {sorted(applicable)}"
            )
    media_urls = source.get("media_urls")
    if media_urls is not None:
        media_url_map = require_mapping(media_urls, f"{label}.media_urls")
        if set(media_url_map) - media_kinds:
            raise ValueError(f"{label}.media_urls contains unsupported media kinds")
        for media_kind, url in media_url_map.items():
            require_urls([url], f"{label}.media_urls.{media_kind}")
    return source


def load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path, "source catalog")
    if payload.get("schema_version") != 3:
        raise ValueError("source catalog schema_version must be 3")
    values = payload.get("sources")
    if not isinstance(values, list) or not values:
        raise ValueError("source catalog sources must be a non-empty list")
    catalog: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        source = validate_source_definition(
            require_mapping(value, f"source catalog item {index}"),
            f"source catalog item {index}",
        )
        source_id = source["id"]
        if source_id == "x" or source.get("name") == "X":
            raise ValueError("X must not appear in the source catalog")
        if source_id in catalog:
            raise ValueError(f"source catalog contains duplicate id: {source_id}")
        catalog[source_id] = source
    return catalog


def is_applicable(
    source: dict[str, Any], material_type: str, media_kinds: set[str]
) -> bool:
    return bool(set(source.get("media_kinds", [])) & media_kinds) and (
        material_type in {"mixed", "custom"}
        or material_type in source.get("applicable_for", [])
    )


def routed_source_ids(
    catalog: dict[str, dict[str, Any]],
    material_type: str,
    media_kinds: set[str],
    access_modes: set[str],
) -> set[str]:
    return {
        source_id
        for source_id, source in catalog.items()
        if source.get("access_mode") in access_modes
        and is_applicable(source, material_type, media_kinds)
    }


def validate_custom_sources(
    values: Any, requested_media: set[str]
) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise ValueError("manual_enhancement.custom_sources must be a list")
    custom: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        source = validate_source_definition(
            require_mapping(value, f"manual_enhancement.custom_sources[{index}]"),
            f"manual_enhancement.custom_sources[{index}]",
            custom=True,
        )
        source_id = source["id"]
        if not source_id.startswith("custom-"):
            raise ValueError("custom source ids must start with custom-")
        if source_id in custom:
            raise ValueError(f"duplicate custom source id: {source_id}")
        if not set(source["media_kinds"]) <= requested_media:
            raise ValueError("custom source media kinds must be requested for this run")
        custom[source_id] = source
    return custom


def index_source_records(
    payload: dict[str, Any], expected_ids: set[str]
) -> dict[str, dict[str, Any]]:
    values = payload.get("sources")
    if not isinstance(values, list):
        raise ValueError("sources must be a list")
    records: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(values):
        record = require_mapping(value, f"sources[{index}]")
        source_id = require_text(record.get("source_id"), f"sources[{index}].source_id")
        if source_id not in expected_ids:
            raise ValueError(f"unknown source_id: {source_id}")
        if source_id in records:
            raise ValueError(f"duplicate source record: {source_id}")
        records[source_id] = record
    missing = sorted(expected_ids - set(records))
    if missing:
        raise ValueError("missing source records: " + ", ".join(missing))
    return records


def validate_visible_samples(
    record: dict[str, Any],
    source_id: str,
    source: dict[str, Any],
    requested_media: set[str],
) -> set[str]:
    values = record.get("visible_samples")
    if not isinstance(values, list) or not values:
        raise ValueError(
            f"{source_id}.visible_samples must contain actual visible image/video samples"
        )
    allowed_kinds = set(source["media_kinds"]) & requested_media
    visible_kinds: set[str] = set()
    for index, value in enumerate(values):
        sample = require_mapping(value, f"{source_id}.visible_samples[{index}]")
        require_urls([sample.get("url")], f"{source_id}.visible_samples[{index}].url")
        media_kind = require_text(
            sample.get("media_kind"), f"{source_id}.visible_samples[{index}].media_kind"
        )
        if media_kind not in allowed_kinds:
            raise ValueError(
                f"{source_id} visible sample has unsuitable media_kind: {media_kind}"
            )
        visibility = sample.get("visibility")
        if media_kind == "video":
            if visibility != "video-playback":
                raise ValueError(
                    f"{source_id} video sample visibility must be video-playback"
                )
        elif source_id == "google-images":
            if visibility not in {"enlarged-preview", "full-image"}:
                raise ValueError(
                    "google-images photo evidence must be an enlarged-preview "
                    "or full-image; thumbnails do not count"
                )
            require_urls(
                [sample.get("origin_url")],
                f"{source_id}.visible_samples[{index}].origin_url",
            )
        elif visibility != "full-image":
            raise ValueError(
                f"{source_id} photo sample visibility must be full-image; "
                "page-only and thumbnails do not count"
            )
        require_text(
            sample.get("observation"),
            f"{source_id}.visible_samples[{index}].observation",
        )
        visible_kinds.add(media_kind)
    return visible_kinds


def validate_observed_source(
    record: dict[str, Any],
    source_id: str,
    source: dict[str, Any],
    requested_media: set[str],
) -> set[str]:
    if record.get("calibration_use") != "used":
        raise ValueError(f"accessed source {source_id} must set calibration_use used")
    require_timestamp(record.get("accessed_at"), f"{source_id}.accessed_at")
    require_text_list(record.get("search_terms"), f"{source_id}.search_terms")
    require_text(record.get("sample_scope"), f"{source_id}.sample_scope")
    require_text(record.get("discovery_mechanism"), f"{source_id}.discovery_mechanism")
    require_text(record.get("access_limitations"), f"{source_id}.access_limitations")
    visible_kinds = validate_visible_samples(
        record, source_id, source, requested_media
    )
    roles = set(require_text_list(record.get("roles"), f"{source_id}.roles"))
    if roles - set(source["roles"]):
        raise ValueError(f"{source_id}.roles must match catalog/custom roles")
    require_text_list(record.get("keywords"), f"{source_id}.keywords")
    patterns = require_mapping(record.get("patterns"), f"{source_id}.patterns")
    if not patterns:
        raise ValueError(f"{source_id}.patterns must contain observed patterns")
    for dimension, observation in patterns.items():
        if dimension not in PATTERN_DIMENSIONS:
            raise ValueError(f"{source_id}.patterns has unknown dimension: {dimension}")
        require_text(observation, f"{source_id}.patterns.{dimension}")
    return visible_kinds


def validate_failed_source(record: dict[str, Any], source_id: str) -> None:
    if record.get("calibration_use") != "skipped":
        raise ValueError(f"failed source {source_id} must set calibration_use skipped")
    require_timestamp(record.get("accessed_at"), f"{source_id}.accessed_at")
    require_text_list(record.get("search_terms"), f"{source_id}.search_terms")
    require_urls(record.get("attempted_urls"), f"{source_id}.attempted_urls")
    require_text(record.get("access_limitations"), f"{source_id}.access_limitations")
    require_text(record.get("failure_reason"), f"{source_id}.failure_reason")
    if record.get("visible_samples") != []:
        raise ValueError(f"failed source {source_id} must have empty visible_samples")


def validate_source_records(
    records: dict[str, dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
    requested_media: set[str],
    selected_automatic: set[str],
    selected_manual: set[str],
) -> tuple[
    dict[str, set[str]],
    dict[str, set[str]],
    set[str],
    set[str],
]:
    automatic_success = {media_kind: set() for media_kind in requested_media}
    manual_success = {media_kind: set() for media_kind in requested_media}
    all_success: set[str] = set()
    manual_failed: set[str] = set()
    selected = selected_automatic | selected_manual
    for source_id, record in records.items():
        source = catalog[source_id]
        access_mode = source["access_mode"]
        if record.get("access_mode") != access_mode:
            raise ValueError(f"{source_id}.access_mode must match its source definition")
        if source_id not in selected:
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
        if status == "failed":
            validate_failed_source(record, source_id)
            if access_mode == "automatic":
                if record.get("authentication_used") is not False:
                    raise ValueError(
                        f"automatic source {source_id} must not use authentication"
                    )
            else:
                if record.get("user_visible_browser") is not True:
                    raise ValueError(
                        f"manual source {source_id} must use the user's visible browser"
                    )
                manual_failed.add(source_id)
            continue
        if status != "accessed":
            raise ValueError(f"selected source {source_id} must be accessed or failed")
        visible_kinds = validate_observed_source(
            record, source_id, source, requested_media
        )
        if access_mode == "automatic":
            if record.get("authentication_used") is not False:
                raise ValueError(
                    f"automatic source {source_id} must require no authentication"
                )
            for media_kind in visible_kinds:
                automatic_success[media_kind].add(source_id)
        else:
            if record.get("user_visible_browser") is not True:
                raise ValueError(
                    f"manual source {source_id} must be observed in the user's visible browser"
                )
            for media_kind in visible_kinds:
                manual_success[media_kind].add(source_id)
        all_success.add(source_id)
    return automatic_success, manual_success, all_success, manual_failed


def validate_observation_list(
    value: Any,
    label: str,
    allowed_source_ids: set[str],
    *,
    allow_empty: bool,
    cross_source: bool = False,
    required_role: str | None = None,
    catalog: dict[str, dict[str, Any]] | None = None,
) -> None:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(
            f"{label} must be {'a list' if allow_empty else 'a non-empty list'}"
        )
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
        if not source_ids:
            raise ValueError(f"{label}[{index}] must cite visible evidence")
        unknown = sorted(source_ids - allowed_source_ids)
        if unknown:
            raise ValueError(f"{label}[{index}] cites unavailable sources: {unknown}")
        if cross_source and len(source_ids) < 2:
            raise ValueError(f"{label}[{index}] must cite at least two visible sources")
        if required_role and catalog:
            invalid = sorted(
                source_id
                for source_id in source_ids
                if required_role not in catalog[source_id].get("roles", [])
            )
            if invalid:
                raise ValueError(
                    f"{label}[{index}] must cite {required_role} sources; invalid: {invalid}"
                )


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
        automatic_success | manual_success,
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
        raise ValueError(
            "calibration summary is missing pattern dimensions: " + ", ".join(missing)
        )
    for dimension in PATTERN_DIMENSIONS:
        require_text(
            dimensions.get(dimension),
            f"calibration_summary.pattern_dimensions.{dimension}",
        )
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")
    require_text(
        summary.get("calibration_state_note"),
        "calibration_summary.calibration_state_note",
    )


def validate_static_summary(payload: dict[str, Any]) -> None:
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
    summary = require_mapping(payload.get("calibration_summary"), "calibration_summary")
    long_term = summary.get("long_term_standards")
    if not isinstance(long_term, list) or not long_term:
        raise ValueError("static calibration requires long_term_standards")
    for index, item in enumerate(long_term):
        observation = require_mapping(
            item, f"calibration_summary.long_term_standards[{index}]"
        )
        require_text(
            observation.get("observation"),
            f"calibration_summary.long_term_standards[{index}].observation",
        )
        require_text_list(
            observation.get("source_ids", []),
            f"calibration_summary.long_term_standards[{index}].source_ids",
            allow_empty=True,
        )
    for field in (
        "recent_platform_trends",
        "author_style_signals",
        "cross_source_patterns",
    ):
        if summary.get(field) != []:
            raise ValueError(
                f"static-authorized mode cannot claim live {field.replace('_', ' ')}"
            )
    require_text_list(
        summary.get("applied_selection_rules"),
        "calibration_summary.applied_selection_rules",
    )
    require_mapping(
        summary.get("pattern_dimensions"),
        "calibration_summary.pattern_dimensions",
    )
    require_text(summary.get("popularity_use"), "calibration_summary.popularity_use")
    require_text(
        summary.get("calibration_state_note"),
        "calibration_summary.calibration_state_note",
    )


def validate(payload: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> str:
    reject_sensitive_fields(payload)
    if payload.get("schema_version") != 3:
        raise ValueError("schema_version must be 3")
    material_type = require_text(payload.get("material_type"), "material_type")
    if material_type not in MATERIAL_TYPES:
        raise ValueError(f"unsupported material_type: {material_type}")
    media_kind_list = require_text_list(payload.get("media_kinds"), "media_kinds")
    requested_media = set(media_kind_list)
    if requested_media - MEDIA_KINDS:
        raise ValueError("media_kinds must contain only photo/video values")

    selected_automatic = routed_source_ids(
        catalog, material_type, requested_media, {"automatic"}
    )
    offered_manual = routed_source_ids(
        catalog,
        material_type,
        requested_media,
        {"manual-challenge", "manual-login"},
    )

    manual = require_mapping(payload.get("manual_enhancement"), "manual_enhancement")
    manual_status = require_text(manual.get("status"), "manual_enhancement.status")
    if manual_status not in MANUAL_STATES:
        raise ValueError(f"unsupported manual enhancement status: {manual_status}")
    manual_mode = require_text(manual.get("mode"), "manual_enhancement.mode")
    if manual_mode not in MANUAL_MODES:
        raise ValueError(f"unsupported manual enhancement mode: {manual_mode}")
    require_exact_id_set(
        manual.get("offered_source_ids"),
        offered_manual,
        "manual_enhancement.offered_source_ids",
    )
    custom_catalog = validate_custom_sources(
        manual.get("custom_sources"), requested_media
    )
    effective_catalog = dict(catalog)
    overlap = set(effective_catalog) & set(custom_catalog)
    if overlap:
        raise ValueError(f"custom source ids collide with catalog: {sorted(overlap)}")
    effective_catalog.update(custom_catalog)
    selected_manual = set(
        require_text_list(
            manual.get("selected_source_ids"),
            "manual_enhancement.selected_source_ids",
            allow_empty=True,
        )
    )
    if len(selected_manual) > 1:
        raise ValueError("manual enhancement recommends and selects at most one source")
    if selected_manual - (offered_manual | set(custom_catalog)):
        raise ValueError("manual enhancement selected an unavailable source")
    readiness = manual.get("user_readiness_confirmed")
    require_text(manual.get("detail"), "manual_enhancement.detail")

    expected_access = {
        "challenge": "manual-challenge",
        "login": "manual-login",
        "custom": "manual-custom",
    }
    if manual_mode == "none":
        if manual_status != "declined" or selected_manual or custom_catalog:
            raise ValueError("manual mode none must be declined with no selected/custom source")
        if readiness is not False:
            raise ValueError("declined manual enhancement must not claim readiness")
    else:
        if len(selected_manual) != 1:
            raise ValueError("manual enhancement requires exactly one selected source")
        selected_id = next(iter(selected_manual))
        if effective_catalog[selected_id]["access_mode"] != expected_access[manual_mode]:
            raise ValueError("manual source access mode does not match the selected manual mode")
        if manual_mode == "custom" and set(custom_catalog) != selected_manual:
            raise ValueError("custom mode must define exactly the selected custom source")
        if manual_mode != "custom" and custom_catalog:
            raise ValueError("catalog manual modes cannot define custom sources")
        if manual_status == "completed" and readiness is not True:
            raise ValueError("completed manual enhancement requires user readiness")

    records = index_source_records(payload, set(effective_catalog))
    automatic_success_by_kind, manual_success_by_kind, all_success, manual_failed = (
        validate_source_records(
            records,
            effective_catalog,
            requested_media,
            selected_automatic,
            selected_manual,
        )
    )
    visible_manual_ids = set().union(*manual_success_by_kind.values())
    if manual_status == "completed" and not visible_manual_ids:
        raise ValueError("completed manual enhancement requires visible manual evidence")
    if manual_status == "cannot-use" and visible_manual_ids:
        raise ValueError("cannot-use manual enhancement cannot contain visible evidence")
    if manual_status == "declined" and (selected_manual or visible_manual_ids):
        raise ValueError("declined manual enhancement cannot select or use a source")
    if manual_status == "cannot-use" and selected_manual - manual_failed:
        raise ValueError("cannot-use manual enhancement must record the selected source failure")

    automatic = require_mapping(
        payload.get("automatic_calibration"), "automatic_calibration"
    )
    require_timestamp(
        automatic.get("checked_at"), "automatic_calibration.checked_at"
    )
    require_text(automatic.get("detail"), "automatic_calibration.detail")
    media_results = require_mapping(
        automatic.get("media"), "automatic_calibration.media"
    )
    if set(media_results) != requested_media:
        raise ValueError("automatic_calibration.media must match requested media_kinds")

    final_ready = True
    final_counts: dict[str, int] = {}
    for media_kind in sorted(requested_media):
        result = require_mapping(
            media_results[media_kind],
            f"automatic_calibration.media.{media_kind}",
        )
        require_text(
            result.get("detail"),
            f"automatic_calibration.media.{media_kind}.detail",
        )
        automatic_applicable = {
            source_id
            for source_id in selected_automatic
            if media_kind in effective_catalog[source_id]["media_kinds"]
        }
        successful = automatic_success_by_kind[media_kind]
        failed = automatic_applicable - successful
        require_exact_id_set(
            result.get("successful_source_ids"),
            successful,
            f"automatic_calibration.media.{media_kind}.successful_source_ids",
        )
        require_exact_id_set(
            result.get("failed_source_ids"),
            failed,
            f"automatic_calibration.media.{media_kind}.failed_source_ids",
        )
        expected_state = (
            "ready" if len(successful) >= 2 else "partial" if successful else "unavailable"
        )
        state = require_text(
            result.get("status"),
            f"automatic_calibration.media.{media_kind}.status",
        )
        if state != expected_state:
            raise ValueError(
                f"automatic_calibration.media.{media_kind}.status must be {expected_state}"
            )
        combined = successful | manual_success_by_kind[media_kind]
        final_counts[media_kind] = len(combined)
        final_ready = final_ready and len(combined) >= 2

    calibration_mode = require_text(payload.get("calibration_mode"), "calibration_mode")
    static_authorized = payload.get("static_fallback_authorized")
    automatic_ids = set().union(*automatic_success_by_kind.values())
    manual_ids = set().union(*manual_success_by_kind.values())
    if final_ready:
        if static_authorized is not False:
            raise ValueError("ready live calibration cannot claim static fallback")
        expected_mode = (
            "manual-enhanced" if manual_status == "completed" else "automatic"
        )
        if calibration_mode != expected_mode:
            raise ValueError(f"ready calibration_mode must be {expected_mode}")
        validate_ready_summary(
            payload, effective_catalog, automatic_ids, manual_ids
        )
        return f"ready-{expected_mode}"

    overall_state = "partial" if any(final_counts.values()) else "unavailable"
    if static_authorized is True:
        if calibration_mode != "static-authorized":
            raise ValueError("authorized fallback requires calibration_mode static-authorized")
        validate_static_summary(payload)
        return f"ready-static-authorized-{overall_state}"
    if static_authorized is not False or calibration_mode != overall_state:
        raise ValueError(
            f"incomplete per-media calibration must remain {overall_state} until authorization"
        )
    return f"paused-{overall_state}"


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
        print(f"{status}: {PARTIAL_NOTICE}", file=sys.stderr)
        return 3
    if status == "paused-unavailable":
        print(f"{status}: {UNAVAILABLE_NOTICE}", file=sys.stderr)
        return 3
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
