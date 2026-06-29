"""Tests for the Import Upload REST API endpoints.

Covers:
  - POST /import/upload (generic multipart upload)
  - POST /import/zip (ZIP archive upload)
  - POST /import/csv (dedicated CSV upload)
  - GET /import/status/{job_id}
  - GET /import/history
  - GET /import/report/{job_id}
  - Error handling (bad extensions, missing files, etc.)
"""

from __future__ import annotations

import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient


class TestImportUploadEndpoints:
    """POST /api/v1/import/upload — generic file upload."""

    def test_upload_csv_incident(self, client: TestClient) -> None:
        csv_content = "incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Cooling failure\n"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("incidents.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] is not None
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["summary"]["classification"]["category"] == "INCIDENT"

    def test_upload_csv_complaint(self, client: TestClient) -> None:
        csv_content = "complaint_id,customer_id,date,severity,issue\nCMP001,CUS001,2026-06-01,High,Overheating\n"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("complaints.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["classification"]["category"] == "COMPLAINT"
        assert data["summary"]["evidence_generated"] > 0

    def test_upload_csv_equipment(self, client: TestClient) -> None:
        csv_content = "asset_id,asset_name,asset_type,customer_id\nAST001,Transformer A,Transformer,CUS001\n"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("equipment.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["classification"]["category"] == "EQUIPMENT"

    def test_upload_json_rules(self, client: TestClient) -> None:
        json_content = json.dumps([{"rule_id": "R001", "category": "Safety", "condition": "temp > 90", "action": "Shutdown", "severity": "Critical"}])
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("rules.json", json_content, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["summary"]["classification"]["category"] == "BUSINESS_RULE"

    def test_upload_txt_knowledge(self, client: TestClient) -> None:
        txt_content = "Energy saving tips: turn off lights when not in use."
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("energy_tips.txt", txt_content, "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["summary"]["evidence_generated"] >= 0

    def test_upload_pdf(self, client: TestClient) -> None:
        pdf_content = b"%PDF-1.4 fake PDF content"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("manual.pdf", pdf_content, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["summary"]["classification"]["category"] == "PDF_MANUAL"

    def test_upload_unsupported_extension(self, client: TestClient) -> None:
        content = b"some binary content"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("data.exe", content, "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.text

    def test_upload_csv_unknown_headers(self, client: TestClient) -> None:
        csv_content = "foo,bar,baz\n1,2,3\n"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("unknown.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_upload_triggers_reasoning_and_nba(self, client: TestClient) -> None:
        csv_content = "incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Cooling failure\n"
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("incidents.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        summary = data["summary"]
        assert summary["reasoning_triggered"] is True
        assert summary["recommendations_generated"] is True

    def test_upload_json_recommendation(self, client: TestClient) -> None:
        json_content = json.dumps([{"recommendation_id": "REC001", "incident_id": "INC001", "asset_id": "AST001", "recommendation": "Replace fan"}])
        response = client.post(
            "/api/v1/import/upload",
            files={"file": ("recommendations.json", json_content, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["summary"]["classification"]["category"] == "SCENARIO_OUTCOME"


class TestImportZipEndpoint:
    """POST /api/v1/import/zip — ZIP archive upload."""

    def test_upload_zip_with_csv(self, client: TestClient) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("incidents.csv", "incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Cooling failure\n")
            zf.writestr("complaints.csv", "complaint_id,customer_id,date,severity,issue\nCMP001,CUS001,2026-06-01,High,Noise\n")
        buf.seek(0)

        response = client.post(
            "/api/v1/import/zip",
            files={"file": ("dataset.zip", buf.getvalue(), "application/zip")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["summary"]["files_processed"] == 2
        assert data["summary"]["total_imported"] > 0
        assert data["summary"]["reasoning_triggered"] is True
        assert data["summary"]["recommendations_generated"] is True

    def test_upload_zip_file_details(self, client: TestClient) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("incidents.csv", "incident_id,asset_id,severity\nI001,A001,High\n")
            zf.writestr("energy_tips.txt", "Save energy!")
        buf.seek(0)

        response = client.post(
            "/api/v1/import/zip",
            files={"file": ("data.zip", buf.getvalue(), "application/zip")},
        )
        assert response.status_code == 200
        data = response.json()
        details = data["summary"]["file_details"]
        assert len(details) == 2
        categories = {d["category"] for d in details}
        assert "INCIDENT" in categories
        assert "BUSINESS_DOCUMENT" in categories or "SCENARIO_INCIDENT" in categories

    def test_upload_non_zip_returns_400(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/import/zip",
            files={"file": ("data.csv", "a,b,c\n1,2,3\n", "text/csv")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.text

    def test_upload_empty_zip(self, client: TestClient) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            pass
        buf.seek(0)

        response = client.post(
            "/api/v1/import/zip",
            files={"file": ("empty.zip", buf.getvalue(), "application/zip")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["files_processed"] == 0


class TestImportCsvEndpoint:
    """POST /api/v1/import/csv — dedicated CSV upload."""

    def test_upload_csv_direct(self, client: TestClient) -> None:
        csv_content = "incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Cooling failure\n"
        response = client.post(
            "/api/v1/import/csv",
            files={"file": ("report.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] is not None
        assert data["status"] == "completed"
        assert data["summary"]["classification"]["category"] == "INCIDENT"
        assert data["summary"]["reasoning_triggered"] is True
        assert data["summary"]["recommendations_generated"] is True

    def test_upload_csv_with_complaints(self, client: TestClient) -> None:
        csv_content = "complaint_id,customer_id,date,severity,issue\nCMP001,CUS001,2026-06-01,High,Overheating\nCMP002,CUS001,2026-06-02,Medium,Noise\n"
        response = client.post(
            "/api/v1/import/csv",
            files={"file": ("complaints.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["classification"]["category"] == "COMPLAINT"
        assert data["summary"]["rows_imported"] == 2
        assert data["summary"]["evidence_generated"] == 2

    def test_upload_non_csv_returns_400(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/import/csv",
            files={"file": ("data.json", '{"key": "value"}', "application/json")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.text


class TestImportStatusEndpoint:
    """GET /api/v1/import/status/{job_id}."""

    def test_get_job_status_after_upload(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/import/upload",
            files={"file": ("test.csv", "incident_id,severity\nI001,High\n", "text/csv")},
        )
        job_id = resp.json()["job_id"]

        response = client.get(f"/api/v1/import/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["filename"] == "test.csv"

    def test_get_status_nonexistent_job(self, client: TestClient) -> None:
        response = client.get("/api/v1/import/status/nonexistent123")
        assert response.status_code == 404


class TestImportHistoryEndpoint:
    """GET /api/v1/import/history."""

    def test_list_history(self, client: TestClient) -> None:
        client.post(
            "/api/v1/import/upload",
            files={"file": ("a.csv", "incident_id,severity\nI001,High\n", "text/csv")},
        )
        client.post(
            "/api/v1/import/upload",
            files={"file": ("b.csv", "incident_id,severity\nI002,Low\n", "text/csv")},
        )

        response = client.get("/api/v1/import/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["jobs"]) >= 2

    def test_history_pagination(self, client: TestClient) -> None:
        response = client.get("/api/v1/import/history?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) <= 1

    def test_history_defaults(self, client: TestClient) -> None:
        response = client.get("/api/v1/import/history")
        assert response.status_code == 200
        assert "total" in response.json()


class TestImportReportEndpoint:
    """GET /api/v1/import/report/{job_id}."""

    def test_get_report_after_upload(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/import/upload",
            files={"file": ("test.csv", "incident_id,severity\nI001,High\n", "text/csv")},
        )
        job_id = resp.json()["job_id"]

        response = client.get(f"/api/v1/import/report/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["classification"] is not None
        assert data["import_summary"] is not None
        assert data["recommendations"] is not None

    def test_get_report_nonexistent(self, client: TestClient) -> None:
        response = client.get("/api/v1/import/report/bad123")
        assert response.status_code == 404

    def test_full_report_fields(self, client: TestClient) -> None:
        csv_content = "complaint_id,customer_id,date,severity,issue\nCMP001,CUS001,2026-06-01,High,Overheating\nCMP002,CUS001,2026-06-02,Medium,Noise\n"
        resp = client.post(
            "/api/v1/import/csv",
            files={"file": ("complaints.csv", csv_content, "text/csv")},
        )
        job_id = resp.json()["job_id"]

        response = client.get(f"/api/v1/import/report/{job_id}")
        data = response.json()
        assert data["classification"]["category"] == "COMPLAINT"
        assert data["import_summary"]["rows_imported"] == 2
        assert data["recommendations"]["reasoning"] is True
        assert data["recommendations"]["next_best_action"] is True


class TestRouterRegistration:
    """Verify the import router is registered correctly."""

    def test_import_router_prefix(self) -> None:
        from adip.api.rest.routers import router as main_router
        route_paths = {route.path for route in main_router.routes}
        assert "/api/v1/import/upload" in route_paths
        assert "/api/v1/import/zip" in route_paths
        assert "/api/v1/import/csv" in route_paths
        assert "/api/v1/import/status/{job_id}" in route_paths
        assert "/api/v1/import/history" in route_paths
        assert "/api/v1/import/report/{job_id}" in route_paths

    def test_import_endpoints_return_200(self, client: TestClient) -> None:
        endpoints = [
            ("POST", "/api/v1/import/csv"),
            ("POST", "/api/v1/import/zip"),
            ("POST", "/api/v1/import/upload"),
        ]
        for method, path in endpoints:
            response = getattr(client, method.lower())(path)
            assert response.status_code in (200, 400, 422)
            assert response.status_code != 404
