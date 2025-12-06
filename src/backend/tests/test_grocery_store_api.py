"""
Tests for Grocery Store CRUD API
"""

from models import seed_defaults


class TestGroceryStoreListAndCreate:
    """Tests for list and create grocery store endpoints"""

    def test_list_grocery_stores_returns_seeded_default(self, client, session):
        """GET returns the seeded default store on fresh DB"""
        seed_defaults(session)

        response = client.get("/api/config/grocery-stores")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Grocery Store"
        assert data[0]["description"] == "Default grocery store for shopping lists"
        assert "id" in data[0]
        assert "created_at" in data[0]

    def test_create_grocery_store_returns_new_store_with_id(self, client, session):
        """POST creates new store and returns it with ID"""
        seed_defaults(session)

        response = client.post(
            "/api/config/grocery-stores",
            json={"name": "Costco", "description": "Bulk shopping"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Costco"
        assert data["description"] == "Bulk shopping"
        assert "id" in data
        assert "created_at" in data

        # Verify it appears in list
        list_response = client.get("/api/config/grocery-stores")
        assert len(list_response.json()) == 2

    def test_list_grocery_stores_ordered_by_created_at(self, client, session):
        """GET returns stores ordered by created_at (oldest first)"""
        seed_defaults(session)

        # Create additional stores
        client.post(
            "/api/config/grocery-stores",
            json={"name": "Costco", "description": "Bulk"},
        )
        client.post(
            "/api/config/grocery-stores",
            json={"name": "Co-op", "description": "Local"},
        )

        response = client.get("/api/config/grocery-stores")
        data = response.json()

        assert len(data) == 3
        # First store should be the seeded default (oldest)
        assert data[0]["name"] == "Grocery Store"
        assert data[1]["name"] == "Costco"
        assert data[2]["name"] == "Co-op"


class TestGroceryStoreReadUpdateDelete:
    """Tests for get, update, delete grocery store endpoints"""

    def test_get_grocery_store_by_id(self, client, session):
        """GET by id returns the specific store"""
        seed_defaults(session)

        # Get list to find the ID
        list_response = client.get("/api/config/grocery-stores")
        store_id = list_response.json()[0]["id"]

        response = client.get(f"/api/config/grocery-stores/{store_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == store_id
        assert data["name"] == "Grocery Store"

    def test_get_grocery_store_not_found_returns_404(self, client, session):
        """GET by id with non-existent ID returns 404"""
        seed_defaults(session)

        response = client.get("/api/config/grocery-stores/9999")

        assert response.status_code == 404

    def test_update_grocery_store_modifies_fields(self, client, session):
        """PUT updates the store fields"""
        seed_defaults(session)

        # Get list to find the ID
        list_response = client.get("/api/config/grocery-stores")
        store_id = list_response.json()[0]["id"]

        response = client.put(
            f"/api/config/grocery-stores/{store_id}",
            json={"name": "Cub Foods", "description": "Updated description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cub Foods"
        assert data["description"] == "Updated description"

        # Verify persisted
        get_response = client.get(f"/api/config/grocery-stores/{store_id}")
        assert get_response.json()["name"] == "Cub Foods"

    def test_update_grocery_store_partial_update(self, client, session):
        """PUT with partial fields only updates provided fields"""
        seed_defaults(session)

        list_response = client.get("/api/config/grocery-stores")
        store_id = list_response.json()[0]["id"]

        # Only update name
        response = client.put(
            f"/api/config/grocery-stores/{store_id}",
            json={"name": "New Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        # Description should be unchanged
        assert data["description"] == "Default grocery store for shopping lists"

    def test_delete_grocery_store_removes_record(self, client, session):
        """DELETE removes the store"""
        seed_defaults(session)

        # Create a second store so we can delete one
        client.post(
            "/api/config/grocery-stores",
            json={"name": "Costco", "description": "Bulk"},
        )

        list_response = client.get("/api/config/grocery-stores")
        assert len(list_response.json()) == 2
        store_id = list_response.json()[1]["id"]  # Delete the second one

        response = client.delete(f"/api/config/grocery-stores/{store_id}")

        assert response.status_code == 204

        # Verify removed from list
        list_response = client.get("/api/config/grocery-stores")
        assert len(list_response.json()) == 1

    def test_delete_last_grocery_store_returns_400(self, client, session):
        """DELETE on last store returns 400 (at least one must exist)"""
        seed_defaults(session)

        # Only one store exists
        list_response = client.get("/api/config/grocery-stores")
        assert len(list_response.json()) == 1
        store_id = list_response.json()[0]["id"]

        response = client.delete(f"/api/config/grocery-stores/{store_id}")

        assert response.status_code == 400
        assert "at least one" in response.json()["detail"].lower()

        # Verify store still exists
        list_response = client.get("/api/config/grocery-stores")
        assert len(list_response.json()) == 1
