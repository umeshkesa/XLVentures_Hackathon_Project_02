"""Tests for Interaction API routers."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestInteractionEndpoints:
    def test_list_interactions(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["items"]) > 0

    def test_list_interactions_with_type_filter(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions?type=email")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for item in data["data"]["items"]:
            assert item["type"] == "email"

    def test_list_interactions_with_status_filter(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions?status=escalated")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for item in data["data"]["items"]:
            assert item["status"] == "escalated"

    def test_list_interactions_with_search(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions?search=voltage")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) > 0

    def test_list_interactions_with_pagination(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) <= 5
        assert data["data"]["total"] >= 5

    def test_get_interaction_by_id(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/INT-001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "INT-001"
        assert "subject" in data["data"]
        assert "type" in data["data"]
        assert "customerName" in data["data"]

    def test_get_interaction_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/INT-999")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] is None

    def test_timeline(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/timeline")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "groups" in data["data"]
        assert len(data["data"]["groups"]) > 0
        for group in data["data"]["groups"]:
            assert "date" in group
            assert "interactions" in group
            assert len(group["interactions"]) > 0

    def test_timeline_with_type_filter(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/timeline?type=email")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for group in data["data"]["groups"]:
            for item in group["interactions"]:
                assert item["type"] == "email"

    def test_interaction_has_attachments(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/INT-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["attachments"]) > 0

    def test_interaction_has_related_entities(self, client: TestClient) -> None:
        response = client.get("/api/v1/interactions/INT-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["relatedAssets"]) > 0
        assert len(data["data"]["relatedEvidence"]) > 0
        assert len(data["data"]["relatedRecommendations"]) > 0
