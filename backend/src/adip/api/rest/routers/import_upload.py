"""Import Upload API router — file upload, classification, import pipeline,
evidence generation, reasoning trigger, and NBA recommendation endpoints."""

from __future__ import annotations

import io
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile

from adip.data_import.classifier import ContentClassifier, TargetModule
from adip.data_import.readers import read_csv, read_csv_sample
from adip.data_import.services.post_import import (
    EvidenceIntegrator,
    KnowledgeIntegrator,
    RecommendationIntegrator,
    RulesIntegrator,
    ReasoningTrigger,
    _evidence_service,
    _knowledge_service,
    _rule_service,
    _recommendation_service,
)
from adip.evidence.enums import EvidenceType, EvidenceDomain

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/import", tags=["Import"])

# ── Supported file extensions ──────────────────────────────────────────────

SUPPORTED_EXTENSIONS: set[str] = {".csv", ".json", ".txt", ".pdf", ".zip"}

# ── In-memory job store ───────────────────────────────────────────────────

_jobs: dict[str, dict[str, Any]] = {}
classifier = ContentClassifier()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_job_id() -> str:
    return uuid.uuid4().hex[:12]


def _staging_dir(job_id: str) -> Path:
    d = Path(tempfile.gettempdir()) / "adip_uploads" / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Job helpers ───────────────────────────────────────────────────────────

def _create_job(filename: str, file_type: str) -> str:
    job_id = _make_job_id()
    _jobs[job_id] = {
        "job_id": job_id,
        "filename": filename,
        "file_type": file_type,
        "status": "pending",
        "progress": 0,
        "created_at": _now(),
        "updated_at": _now(),
        "completed_at": None,
        "classification": None,
        "import_summary": None,
        "recommendations": None,
        "error": None,
    }
    return job_id


def _update_job(job_id: str, **updates: Any) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(updates)
        _jobs[job_id]["updated_at"] = _now()


def _get_job_or_404(job_id: str) -> dict[str, Any]:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return job


# ── Integration helpers ───────────────────────────────────────────────────

def _integrate_csv_by_headers(path: Path, category: str) -> int:
    """Read CSV headers and route to the correct evidence integrator."""
    rows = read_csv(path)
    if not rows:
        return 0

    integrator = EvidenceIntegrator()
    category_lower = category.lower()

    mapping: dict[str, tuple[EvidenceType, EvidenceDomain, str, str]] = {
        "incident": (EvidenceType.INCIDENT, EvidenceDomain.MAINTENANCE, "incident_report", "operations"),
        "work_order": (EvidenceType.EMAIL, EvidenceDomain.MAINTENANCE, "work_order", "operations"),
        "maintenance": (EvidenceType.MAINTENANCE, EvidenceDomain.MAINTENANCE, "maintenance", "operations"),
        "alarm": (EvidenceType.SENSOR, EvidenceDomain.OPERATIONS, "alarm", "operations"),
        "complaint": (EvidenceType.CUSTOMER, EvidenceDomain.CUSTOMER, "complaint", "customer"),
        "feedback": (EvidenceType.CUSTOMER, EvidenceDomain.CUSTOMER, "feedback", "customer"),
        "service_request": (EvidenceType.EMAIL, EvidenceDomain.CUSTOMER, "service_request", "customer"),
        "crm_update": (EvidenceType.CRM, EvidenceDomain.CUSTOMER, "crm_update", "customer"),
        "weather": (EvidenceType.SENSOR, EvidenceDomain.OPERATIONS, "weather", "environmental"),
        "sensor_ai4i": (EvidenceType.SENSOR, EvidenceDomain.OPERATIONS, "sensor", "operations"),
        "energy_report": (EvidenceType.REPORT, EvidenceDomain.OPERATIONS, "energy_report", "operations"),
        "equipment": (EvidenceType.SENSOR, EvidenceDomain.MAINTENANCE, "equipment", "asset"),
        "customer_profile": (EvidenceType.CUSTOMER, EvidenceDomain.CUSTOMER, "customer_profile", "reference"),
        "sla": (EvidenceType.REPORT, EvidenceDomain.COMPLIANCE, "sla", "business"),
        "compliance": (EvidenceType.REPORT, EvidenceDomain.COMPLIANCE, "compliance", "business"),
    }

    for key, (ev_type, dom, src, tag) in mapping.items():
        if key in category_lower:
            return integrator.integrate_batch(rows, ev_type, dom, src, tag)

    return integrator.integrate_batch(
        rows, EvidenceType.EMAIL, EvidenceDomain.CUSTOMER, "upload", "imported"
    )


def _integrate_json_content(path: Path, fname: str) -> int:
    """Import JSON content — rules or recommendation history."""
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        data = [data]

    if "rule" in fname.lower() or "rules" in fname.lower():
        integrator = RulesIntegrator()
        return integrator.integrate_rules_json(data)

    if "recommendation" in fname.lower():
        integrator = RecommendationIntegrator()
        return integrator.integrate_history(data)

    integrator = RulesIntegrator()
    return integrator.integrate_rules_json(data)


def _integrate_text_content(path: Path, fname: str) -> int:
    """Import text content as a knowledge document."""
    content = path.read_text(encoding="utf-8")
    if not content:
        return 0

    from adip.knowledge.enums import DocumentType, KnowledgeDomain

    integrator = KnowledgeIntegrator()
    doc = integrator.integrate_document(
        fname, content, DocumentType.ARTICLE, KnowledgeDomain.OPERATIONS,
        title=Path(fname).stem, tags=["uploaded"],
    )
    return 1 if doc else 0


def _integrate_pdf_content(path: Path, fname: str) -> int:
    """Register PDF as a knowledge document."""
    from adip.knowledge.enums import DocumentType, KnowledgeDomain

    content = f"[PDF: {fname}, {path.stat().st_size} bytes - placeholder content]"
    integrator = KnowledgeIntegrator()
    doc = integrator.integrate_document(
        fname, content, DocumentType.PDF, KnowledgeDomain.OPERATIONS,
        title=Path(fname).stem, tags=["pdf", "manual", "uploaded"],
    )
    return 1 if doc else 0


def _process_single_file(path: Path, fname: str) -> dict[str, Any]:
    """Classify and import a single file. Returns integration results."""
    ext = path.suffix.lower()
    result = classifier.classify_file(path)
    category = result.category.value
    route = classifier.route_to_module(result)

    integration: dict[str, Any] = {
        "classification": result.to_dict(),
        "routed_to": route.value,
        "imported_count": 0,
    }

    if ext == ".csv":
        count = _integrate_csv_by_headers(path, category)
        integration["imported_count"] = count
        integration["method"] = "csv_evidence_integration"
    elif ext == ".json":
        count = _integrate_json_content(path, fname)
        integration["imported_count"] = count
        integration["method"] = "json_integration"
    elif ext == ".txt":
        count = _integrate_text_content(path, fname)
        integration["imported_count"] = count
        integration["method"] = "text_knowledge_integration"
    elif ext == ".pdf":
        count = _integrate_pdf_content(path, fname)
        integration["imported_count"] = count
        integration["method"] = "pdf_knowledge_integration"

    return integration


def _process_zip_archive(zip_path: Path) -> list[dict[str, Any]]:
    """Extract and process all files in a ZIP archive."""
    import zipfile

    results: list[dict[str, Any]] = []
    extract_dir = zip_path.parent / f"{zip_path.stem}_extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    for fpath in sorted(extract_dir.rglob("*")):
        if not fpath.is_file():
            continue
        ext = fpath.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS or ext == ".zip":
            continue
        result = _process_single_file(fpath, fpath.name)
        result["original_file"] = str(fpath.relative_to(extract_dir))
        results.append(result)

    return results


def _run_post_import_pipeline(job_id: str) -> dict[str, Any]:
    """Trigger reasoning and NBA generation after all files are imported."""
    trigger = ReasoningTrigger()
    reasoning = trigger.reason_on_evidence(str(uuid.uuid4()), "ENERGY")

    rec_integrator = RecommendationIntegrator()
    nba = rec_integrator.generate_nba({
        "reasoning_result_id": str(uuid.uuid4()),
        "source": "import_upload",
        "incident_id": "upload",
        "asset_id": "upload",
    })

    return {
        "reasoning": reasoning is not None,
        "next_best_action": nba is not None,
        "recommendation_details": str(nba) if nba else None,
    }


# ── Helper: allowed extension check ───────────────────────────────────────

def _validate_extension(filename: str, allowed: set[str] | None = None) -> str:
    ext = Path(filename).suffix.lower()
    check = allowed or SUPPORTED_EXTENSIONS
    if ext not in check:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(check))}",
        )
    return ext


# ── POST /import/upload ──────────────────────────────────────────────────


@router.post("/upload", summary="Upload and import any supported file")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "uploaded_file"
    ext = _validate_extension(filename)
    job_id = _create_job(filename, ext)

    _update_job(job_id, status="processing", progress=10)

    try:
        staging = _staging_dir(job_id)
        dest = staging / filename
        content_bytes = await file.read()
        dest.write_bytes(content_bytes)

        _update_job(job_id, progress=30)

        result = _process_single_file(dest, filename)
        _update_job(job_id, classification=result["classification"], progress=60)

        pipeline = _run_post_import_pipeline(job_id)
        _update_job(job_id, progress=90)

        summary = {
            "file": filename,
            "classification": result["classification"],
            "routed_to": result["routed_to"],
            "imported_count": result["imported_count"],
            "evidence_generated": result["imported_count"],
            "reasoning_triggered": pipeline["reasoning"],
            "recommendations_generated": pipeline["next_best_action"],
        }
        _update_job(
            job_id,
            status="completed",
            progress=100,
            completed_at=_now(),
            import_summary=summary,
            recommendations=pipeline,
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as exc:
        log.exception("import.upload.failed", job_id=job_id, filename=filename)
        _update_job(job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}") from exc


# ── POST /import/zip ──────────────────────────────────────────────────────


@router.post("/zip", summary="Upload and import a ZIP archive")
async def upload_zip(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "archive.zip"
    _validate_extension(filename, {".zip"})
    job_id = _create_job(filename, ".zip")

    _update_job(job_id, status="extracting", progress=10)

    try:
        staging = _staging_dir(job_id)
        dest = staging / filename
        content_bytes = await file.read()
        dest.write_bytes(content_bytes)

        _update_job(job_id, progress=20)

        file_results = _process_zip_archive(dest)
        _update_job(job_id, progress=60)

        pipeline = _run_post_import_pipeline(job_id)
        _update_job(job_id, progress=90)

        total_imported = sum(r.get("imported_count", 0) for r in file_results)
        classifications = [r.get("classification") for r in file_results if r.get("classification")]

        summary = {
            "archive": filename,
            "files_processed": len(file_results),
            "total_imported": total_imported,
            "file_details": [
                {
                    "file": r.get("original_file", r.get("classification", {}).get("source_name", "")),
                    "category": r.get("classification", {}).get("category", "UNKNOWN"),
                    "routed_to": r.get("routed_to", ""),
                    "imported_count": r.get("imported_count", 0),
                }
                for r in file_results
            ],
            "evidence_generated": total_imported,
            "reasoning_triggered": pipeline["reasoning"],
            "recommendations_generated": pipeline["next_best_action"],
        }

        _update_job(
            job_id,
            status="completed",
            progress=100,
            completed_at=_now(),
            classification=classifications,
            import_summary=summary,
            recommendations=pipeline,
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as exc:
        log.exception("import.zip.failed", job_id=job_id, filename=filename)
        _update_job(job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Zip import failed: {exc}") from exc


# ── POST /import/csv ──────────────────────────────────────────────────────


@router.post("/csv", summary="Upload and import a CSV file")
async def upload_csv(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "data.csv"
    _validate_extension(filename, {".csv"})
    job_id = _create_job(filename, ".csv")

    _update_job(job_id, status="processing", progress=10)

    try:
        staging = _staging_dir(job_id)
        dest = staging / filename
        content_bytes = await file.read()
        dest.write_bytes(content_bytes)

        _update_job(job_id, progress=30)

        result = _process_single_file(dest, filename)
        _update_job(job_id, classification=result["classification"], progress=60)

        pipeline = _run_post_import_pipeline(job_id)
        _update_job(job_id, progress=90)

        summary = {
            "file": filename,
            "classification": result["classification"],
            "routed_to": result["routed_to"],
            "rows_imported": result["imported_count"],
            "evidence_generated": result["imported_count"],
            "reasoning_triggered": pipeline["reasoning"],
            "recommendations_generated": pipeline["next_best_action"],
        }

        _update_job(
            job_id,
            status="completed",
            progress=100,
            completed_at=_now(),
            import_summary=summary,
            recommendations=pipeline,
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as exc:
        log.exception("import.csv.failed", job_id=job_id, filename=filename)
        _update_job(job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"CSV import failed: {exc}") from exc


# ── GET /import/status/{job_id} ────────────────────────────────────────────


@router.get("/status/{job_id}", summary="Get import job status")
async def get_job_status(job_id: str) -> dict[str, Any]:
    job = _get_job_or_404(job_id)
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job["progress"],
        "filename": job["filename"],
        "file_type": job["file_type"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
        "error": job["error"],
    }


# ── GET /import/history ────────────────────────────────────────────────────


@router.get("/history", summary="List all import jobs")
async def list_jobs(limit: int = 50, offset: int = 0) -> dict[str, Any]:
    all_jobs = sorted(
        _jobs.values(),
        key=lambda j: j["created_at"],
        reverse=True,
    )
    page = all_jobs[offset:offset + limit]
    return {
        "total": len(all_jobs),
        "offset": offset,
        "limit": limit,
        "jobs": [
            {
                "job_id": j["job_id"],
                "filename": j["filename"],
                "file_type": j["file_type"],
                "status": j["status"],
                "progress": j["progress"],
                "created_at": j["created_at"],
                "completed_at": j["completed_at"],
            }
            for j in page
        ],
    }


# ── GET /import/report/{job_id} ────────────────────────────────────────────


@router.get("/report/{job_id}", summary="Get detailed import report")
async def get_job_report(job_id: str) -> dict[str, Any]:
    job = _get_job_or_404(job_id)
    return {
        "job_id": job["job_id"],
        "filename": job["filename"],
        "file_type": job["file_type"],
        "status": job["status"],
        "progress": job["progress"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "completed_at": job["completed_at"],
        "classification": job.get("classification"),
        "import_summary": job.get("import_summary"),
        "recommendations": job.get("recommendations"),
        "error": job.get("error"),
    }
