"""
Tests for PlanningSession CRUD API endpoints
"""


class TestSessionAPI:
    """Tests for /api/sessions endpoints"""

    def test_create_session_with_name(self, client):
        """POST creates a session with provided name"""
        response = client.post("/api/sessions", json={"name": "Week of Dec 1"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Week of Dec 1"
        assert "id" in data
        assert "created_at" in data

    def test_create_session_with_empty_name(self, client):
        """POST with empty name still creates session (client handles auto-name)"""
        response = client.post("/api/sessions", json={"name": ""})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == ""

    def test_list_sessions_empty(self, client):
        """GET returns empty list when no sessions exist"""
        response = client.get("/api/sessions")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_sessions_returns_created(self, client):
        """GET returns sessions after creation"""
        client.post("/api/sessions", json={"name": "Week 1"})
        client.post("/api/sessions", json={"name": "Week 2"})

        response = client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [s["name"] for s in data]
        assert "Week 1" in names
        assert "Week 2" in names

    def test_list_sessions_ordered_by_created_desc(self, client):
        """GET returns sessions newest first"""
        client.post("/api/sessions", json={"name": "First"})
        client.post("/api/sessions", json={"name": "Second"})

        response = client.get("/api/sessions")

        data = response.json()
        assert data[0]["name"] == "Second"
        assert data[1]["name"] == "First"

    def test_get_session_by_id(self, client):
        """GET by ID returns specific session"""
        create_response = client.post("/api/sessions", json={"name": "My Session"})
        session_id = create_response.json()["id"]

        response = client.get(f"/api/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["name"] == "My Session"

    def test_get_session_not_found(self, client):
        """GET by ID returns 404 for non-existent session"""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(f"/api/sessions/{fake_id}")

        assert response.status_code == 404
