"""
Tests for singleton config APIs (HouseholdProfile, Pantry)
"""

from models import DEFAULT_HOUSEHOLD_PROFILE, DEFAULT_PANTRY, seed_defaults


class TestHouseholdProfileAPI:
    """Tests for /api/config/household-profile endpoints"""

    def test_get_household_profile_returns_seeded_default(self, client, session):
        """GET returns the seeded default content on fresh DB"""
        seed_defaults(session)

        response = client.get("/api/config/household-profile")

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == DEFAULT_HOUSEHOLD_PROFILE
        assert "updated_at" in data

    def test_put_household_profile_updates_content(self, client, session):
        """PUT updates the content and returns updated record"""
        seed_defaults(session)
        new_content = "Family of 3, loves Italian food"

        response = client.put(
            "/api/config/household-profile",
            json={"content": new_content},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == new_content
        assert "updated_at" in data

        get_response = client.get("/api/config/household-profile")
        assert get_response.json()["content"] == new_content

    def test_put_household_profile_allows_empty_content(self, client, session):
        """PUT with empty content is allowed (user may clear it)"""
        seed_defaults(session)

        response = client.put(
            "/api/config/household-profile",
            json={"content": ""},
        )

        assert response.status_code == 200
        assert response.json()["content"] == ""


class TestPantryAPI:
    """Tests for /api/config/pantry endpoints"""

    def test_get_pantry_returns_seeded_default(self, client, session):
        """GET returns the seeded default content on fresh DB"""
        seed_defaults(session)

        response = client.get("/api/config/pantry")

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == DEFAULT_PANTRY
        assert "updated_at" in data

    def test_put_pantry_updates_content(self, client, session):
        """PUT updates the content and returns updated record"""
        seed_defaults(session)
        new_content = "Salt, pepper, olive oil, garlic"

        response = client.put(
            "/api/config/pantry",
            json={"content": new_content},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == new_content
        assert "updated_at" in data

        get_response = client.get("/api/config/pantry")
        assert get_response.json()["content"] == new_content

    def test_put_pantry_allows_empty_content(self, client, session):
        """PUT with empty content is allowed (user may clear it)"""
        seed_defaults(session)

        response = client.put(
            "/api/config/pantry",
            json={"content": ""},
        )

        assert response.status_code == 200
        assert response.json()["content"] == ""
