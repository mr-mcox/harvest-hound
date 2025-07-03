from uuid import UUID

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


class TestStoreCreation:
    """Test POST /stores endpoint behavior."""

    def test_create_store_with_valid_data_returns_201_with_store_details(self) -> None:
        """Test that POST /stores with valid data returns 201 with store details."""
        # Given
        store_data = {"name": "CSA Box"}

        # When
        response = client.post("/stores", json=store_data)

        # Then
        assert response.status_code == 201
        response_data = response.json()

        # Should return a valid store with generated UUID
        assert "store_id" in response_data
        assert UUID(response_data["store_id"])  # Should be valid UUID
        assert response_data["name"] == "CSA Box"
        assert response_data["description"] == ""
        assert response_data["infinite_supply"] is False

        # Store should be persisted and retrievable
        stores_response = client.get("/stores")
        assert stores_response.status_code == 200
        stores = stores_response.json()

        # Should find our created store in the list
        created_store = next(
            (
                store
                for store in stores
                if store["store_id"] == response_data["store_id"]
            ),
            None,
        )
        assert created_store is not None
        assert created_store["name"] == "CSA Box"
        assert created_store["item_count"] == 0
