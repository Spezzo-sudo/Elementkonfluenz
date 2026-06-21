"""Basic QA gates for ValueRacer run folders."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "0.1"
ADVISORY_KEYWORDS = [
    "kaufen",
    "verkaufen",
    "jetzt einsteigen",
    "garantierter gewinn",
    "sichere rendite",
    "kein risiko",
    "all in",
    "reich werden",
    "must buy",
    "buy now",
    "sell now",
    "guaranteed profit",
]


@dataclass(frozen=True)
class QACheck:
    name: str
    status: str
    message: str
    error_code: str | None = None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }
        if self.error_code:
            payload["error_code"] = self.error_code
        if self.details:
            payload["details"] = self.details
        return payload


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_invalid_json": True, "path": str(path)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text_blob(*payloads: dict[str, Any] | None) -> str:
    parts: list[str] = []
    for payload in payloads:
        if payload:
            parts.append(json.dumps(payload, ensure_ascii=False).lower())
    return "\n".join(parts)


def check_required_artifacts(run_dir: Path, *, require_youtube: bool) -> QACheck:
    required = [
        "topic_brief.json",
        "sources.json",
        "job_result.json",
        "logs/orchestrator.log",
    ]
    if require_youtube:
        required.extend(["metadata/youtube.json", "publish/youtube_publish_plan.json"])

    missing = [item for item in required if not (run_dir / item).exists()]
    if missing:
        return QACheck(
            name="required_artifacts",
            status="fail",
            error_code="QA_REQUIRED_ARTIFACT_MISSING",
            message="Required run artifacts are missing.",
            details={"missing": missing},
        )
    return QACheck(
        name="required_artifacts",
        status="pass",
        message="Required run artifacts are present.",
        details={"required": required},
    )


def check_json_validity(files: dict[str, dict[str, Any] | None]) -> QACheck:
    invalid = [name for name, payload in files.items() if payload and payload.get("_invalid_json")]
    if invalid:
        return QACheck(
            name="json_validity",
            status="fail",
            error_code="QA_INVALID_JSON",
            message="One or more JSON artifacts could not be parsed.",
            details={"invalid": invalid},
        )
    return QACheck(name="json_validity", status="pass", message="JSON artifacts are parseable.")


def check_topic(topic_brief: dict[str, Any] | None) -> QACheck:
    if not topic_brief:
        return QACheck(
            name="topic",
            status="fail",
            error_code="QA_TOPIC_MISSING",
            message="topic_brief.json is missing or unreadable.",
        )

    missing: list[str] = []
    for key in ["job_id", "title", "hook", "assets", "requires_review"]:
        if key not in topic_brief:
            missing.append(key)

    if missing:
        return QACheck(
            name="topic",
            status="fail",
            error_code="QA_TOPIC_INCOMPLETE",
            message="topic_brief.json is missing required fields.",
            details={"missing": missing},
        )

    if topic_brief.get("requires_review") is not True:
        return QACheck(
            name="topic",
            status="fail",
            error_code="QA_REVIEW_FLAG_MISSING",
            message="topic_brief.json must require review during dry-run stage.",
        )

    return QACheck(name="topic", status="pass", message="Topic brief has required review-safe fields.")


def check_sources(sources: dict[str, Any] | None) -> QACheck:
    if not sources:
        return QACheck(
            name="sources",
            status="fail",
            error_code="QA_SOURCES_MISSING",
            message="sources.json is missing or unreadable.",
        )
    entries = sources.get("sources", [])
    if not isinstance(entries, list) or not entries:
        return QACheck(
            name="sources",
            status="fail",
            error_code="QA_SOURCES_EMPTY",
            message="sources.json does not contain a non-empty sources list.",
        )
    missing_fields: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            missing_fields.append(f"sources[{index}]")
            continue
        for key in ["source_id", "source_type", "name", "retrieved_at"]:
            if key not in entry:
                missing_fields.append(f"sources[{index}].{key}")
    if missing_fields:
        return QACheck(
            name="sources",
            status="fail",
            error_code="QA_SOURCE_FIELD_MISSING",
            message="sources.json entries are missing required fields.",
            details={"missing": missing_fields},
        )
    return QACheck(name="sources", status="pass", message="Sources manifest is present and traceable.")


def check_advisory_language(*payloads: dict[str, Any] | None) -> QACheck:
    blob = text_blob(*payloads)
    flagged = [keyword for keyword in ADVISORY_KEYWORDS if keyword in blob]
    if flagged:
        return QACheck(
            name="advisory_language",
            status="fail",
            error_code="QA_ADVISORY_FLAGGED",
            message="Potential investment-advice language was found.",
            details={"flagged_keywords": flagged},
        )
    return QACheck(name="advisory_language", status="pass", message="No prohibited advisory keywords detected.")


def check_youtube_metadata(metadata: dict[str, Any] | None) -> QACheck:
    if not metadata:
        return QACheck(
            name="youtube_metadata",
            status="warn",
            error_code="QA_YOUTUBE_METADATA_MISSING",
            message="YouTube metadata is missing; skip this warning for non-YouTube runs.",
        )
    required = ["title", "description", "tags", "hashtags", "requires_review"]
    missing = [key for key in required if key not in metadata]
    if missing:
        return QACheck(
            name="youtube_metadata",
            status="fail",
            error_code="QA_YOUTUBE_METADATA_INCOMPLETE",
            message="YouTube metadata is missing required fields.",
            details={"missing": missing},
        )
    if metadata.get("requires_review") is not True:
        return QACheck(
            name="youtube_metadata",
            status="fail",
            error_code="QA_YOUTUBE_REVIEW_FLAGS_INVALID",
            message="YouTube metadata must require review.",
        )
    if metadata.get("ready_to_publish") is True:
        return QACheck(
            name="youtube_metadata",
            status="fail",
            error_code="QA_YOUTUBE_READY_TO_PUBLISH_UNSAFE",
            message="YouTube metadata must not be publish-ready during dry-run stage.",
        )
    return QACheck(name="youtube_metadata", status="pass", message="YouTube metadata is review-gated.")


def check_publish_plan(plan: dict[str, Any] | None) -> QACheck:
    if not plan:
        return QACheck(
            name="publish_plan",
            status="warn",
            error_code="QA_PUBLISH_PLAN_MISSING",
            message="Publish plan is missing; skip this warning for non-platform runs.",
        )
    problems: list[str] = []
    if plan.get("mode") != "dry_run":
        problems.append("mode must be dry_run")
    if plan.get("privacy_status") != "private":
        problems.append("privacy_status must be private")
    if plan.get("ready_to_publish") is not False:
        problems.append("ready_to_publish must be false")
    if plan.get("requires_review") is not True:
        problems.append("requires_review must be true")

    if problems:
        return QACheck(
            name="publish_plan",
            status="fail",
            error_code="QA_PUBLISH_PLAN_UNSAFE",
            message="Publish plan is not safely review-gated.",
            details={"problems": problems},
        )
    return QACheck(name="publish_plan", status="pass", message="Publish plan is private, dry-run, and review-gated.")


def check_job_result(job_result: dict[str, Any] | None) -> QACheck:
    if not job_result:
        return QACheck(
            name="job_result",
            status="fail",
            error_code="QA_JOB_RESULT_MISSING",
            message="job_result.json is missing or unreadable.",
        )
    if job_result.get("ok") is not True:
        return QACheck(
            name="job_result",
            status="fail",
            error_code="QA_JOB_NOT_OK",
            message="job_result.json does not report ok=true.",
        )
    if job_result.get("requires_review") is not True or job_result.get("ready_to_publish") is not False:
        return QACheck(
            name="job_result",
            status="fail",
            error_code="QA_JOB_REVIEW_FLAGS_INVALID",
            message="job_result.json must require review and must not be publish-ready.",
        )
    return QACheck(name="job_result", status="pass", message="Job result is ok and review-gated.")


def check_repetition(topic_brief: dict[str, Any] | None, history_path: Path | None) -> QACheck:
    if not history_path or not history_path.exists() or not topic_brief:
        return QACheck(
            name="repetition",
            status="skipped",
            message="No history file was provided for repetition checks.",
        )
    topic_id = str(topic_brief.get("topic_id", ""))
    if not topic_id:
        return QACheck(name="repetition", status="warn", message="Topic id missing; repetition check is limited.")

    try:
        entries = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except json.JSONDecodeError:
        return QACheck(
            name="repetition",
            status="warn",
            error_code="QA_HISTORY_INVALID",
            message="History file could not be parsed; repetition check skipped.",
        )

    same_topic_entries = [entry for entry in entries if str(entry.get("topic_slug", "")) == topic_id]
    if len(same_topic_entries) > 1:
        return QACheck(
            name="repetition",
            status="warn",
            error_code="QA_TOPIC_REPEATED_IN_HISTORY",
            message="The topic appears more than once in the provided history.",
            details={"topic_id": topic_id, "count": len(same_topic_entries)},
        )
    return QACheck(name="repetition", status="pass", message="No duplicate topic detected in provided history.")


def evaluate_run(run_dir: Path, *, require_youtube: bool = True, history_path: Path | None = None) -> dict[str, Any]:
    topic_brief = read_json(run_dir / "topic_brief.json")
    sources = read_json(run_dir / "sources.json")
    job_result = read_json(run_dir / "job_result.json")
    youtube_metadata = read_json(run_dir / "metadata" / "youtube.json")
    publish_plan = read_json(run_dir / "publish" / "youtube_publish_plan.json")

    files = {
        "topic_brief.json": topic_brief,
        "sources.json": sources,
        "job_result.json": job_result,
        "metadata/youtube.json": youtube_metadata,
        "publish/youtube_publish_plan.json": publish_plan,
    }

    checks = [
        check_required_artifacts(run_dir, require_youtube=require_youtube),
        check_json_validity(files),
        check_topic(topic_brief),
        check_sources(sources),
        check_job_result(job_result),
        check_advisory_language(topic_brief, youtube_metadata, publish_plan),
        check_youtube_metadata(youtube_metadata),
        check_publish_plan(publish_plan),
        check_repetition(topic_brief, history_path),
    ]

    if not require_youtube:
        checks = [
            check for check in checks
            if check.name not in {"youtube_metadata", "publish_plan"}
            or check.status not in {"warn", "fail"}
        ]

    hard_fail = any(check.status == "fail" for check in checks)
    warnings = [check.message for check in checks if check.status == "warn"]
    error_codes = [check.error_code for check in checks if check.error_code]
    job_id = str((topic_brief or job_result or {}).get("job_id", run_dir.name))

    return {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now_iso(),
        "job_id": job_id,
        "ok": not hard_fail,
        "hard_fail": hard_fail,
        "requires_review": True,
        "ready_to_publish": False,
        "checks": [check.to_dict() for check in checks],
        "warnings": warnings,
        "error_codes": error_codes,
    }
