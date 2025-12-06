"""
Tests for inventory API endpoints (parse, bulk, list)
"""

from unittest.mock import MagicMock, patch

from sqlmodel import select

from models import InventoryItem, seed_defaults


def _mock_ingredient(name, quantity, unit, priority, portion_size=None):
    """Create a mock ingredient with proper attribute access."""
    mock = MagicMock()
    mock.name = name
    mock.quantity = quantity
    mock.unit = unit
    mock.priority = priority
    mock.portion_size = portion_size
    return mock


class TestInventoryParseAPI:
    """Tests for POST /api/inventory/parse endpoint"""

    def test_parse_returns_parsed_ingredients(self, client, session):
        """Parse endpoint calls BAML and returns parsed ingredients"""
        seed_defaults(session)

        mock_result = MagicMock()
        mock_result.ingredients = [
            _mock_ingredient("carrot", 2.0, "pound", "Medium"),
            _mock_ingredient("kale", 1.0, "bunch", "Urgent"),
        ]
        mock_result.parsing_notes = "Parsed 2 ingredients"

        with patch("inventory_routes.b.ExtractIngredients", return_value=mock_result):
            response = client.post(
                "/api/inventory/parse",
                json={"free_text": "2 lbs carrots\n1 bunch kale"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredients"]) == 2
        assert data["ingredients"][0]["ingredient_name"] == "carrot"
        assert data["ingredients"][0]["quantity"] == 2.0
        assert data["ingredients"][0]["unit"] == "pound"
        assert data["ingredients"][0]["priority"] == "Medium"
        assert data["ingredients"][1]["ingredient_name"] == "kale"
        assert data["ingredients"][1]["priority"] == "Urgent"
        assert data["parsing_notes"] == "Parsed 2 ingredients"

    def test_parse_passes_configuration_instructions(self, client, session):
        """Parse endpoint passes configuration_instructions to BAML"""
        seed_defaults(session)

        mock_result = MagicMock()
        mock_result.ingredients = [
            _mock_ingredient("ground beef", 3.0, "package", "Medium", "1 pound"),
        ]
        mock_result.parsing_notes = None

        with patch(
            "inventory_routes.b.ExtractIngredients", return_value=mock_result
        ) as mock_extract:
            response = client.post(
                "/api/inventory/parse",
                json={
                    "free_text": "Ground beef x3",
                    "configuration_instructions": "All meat in 1 pound portions",
                },
            )

        assert response.status_code == 200
        # Verify configuration_instructions was passed to BAML
        mock_extract.assert_called_once_with(
            text="Ground beef x3",
            configuration_instructions="All meat in 1 pound portions",
        )
        data = response.json()
        assert data["ingredients"][0]["portion_size"] == "1 pound"

    def test_parse_returns_empty_list_for_no_ingredients(self, client, session):
        """Parse endpoint returns empty list when no ingredients found"""
        seed_defaults(session)

        mock_result = MagicMock()
        mock_result.ingredients = []
        mock_result.parsing_notes = "No ingredients found"

        with patch("inventory_routes.b.ExtractIngredients", return_value=mock_result):
            response = client.post(
                "/api/inventory/parse",
                json={"free_text": "nothing here"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["ingredients"] == []
        assert data["parsing_notes"] == "No ingredients found"


class TestInventoryBulkAPI:
    """Tests for POST /api/inventory/bulk endpoint"""

    def test_bulk_saves_items_to_database(self, client, session):
        """Bulk endpoint saves all items to database"""
        seed_defaults(session)

        response = client.post(
            "/api/inventory/bulk",
            json={
                "items": [
                    {
                        "ingredient_name": "carrot",
                        "quantity": 2.0,
                        "unit": "pound",
                        "priority": "Medium",
                        "portion_size": None,
                    },
                    {
                        "ingredient_name": "kale",
                        "quantity": 1.0,
                        "unit": "bunch",
                        "priority": "Urgent",
                        "portion_size": None,
                    },
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["saved_count"] == 2

        # Verify items are in database
        items = session.exec(select(InventoryItem)).all()
        assert len(items) == 2
        assert items[0].ingredient_name == "carrot"
        assert items[1].ingredient_name == "kale"

    def test_bulk_saves_portion_size(self, client, session):
        """Bulk endpoint correctly saves portion_size field"""
        seed_defaults(session)

        response = client.post(
            "/api/inventory/bulk",
            json={
                "items": [
                    {
                        "ingredient_name": "ground beef",
                        "quantity": 3.0,
                        "unit": "package",
                        "priority": "High",
                        "portion_size": "1 pound",
                    },
                ]
            },
        )

        assert response.status_code == 200
        item = session.exec(select(InventoryItem)).first()
        assert item.portion_size == "1 pound"

    def test_bulk_empty_list_returns_zero(self, client, session):
        """Bulk endpoint handles empty list gracefully"""
        seed_defaults(session)

        response = client.post(
            "/api/inventory/bulk",
            json={"items": []},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["saved_count"] == 0


class TestInventoryListAPI:
    """Tests for GET /api/inventory endpoint"""

    def test_list_returns_all_inventory_items(self, client, session):
        """List endpoint returns all inventory items"""
        seed_defaults(session)

        # Add items via bulk endpoint
        client.post(
            "/api/inventory/bulk",
            json={
                "items": [
                    {
                        "ingredient_name": "carrot",
                        "quantity": 2.0,
                        "unit": "pound",
                        "priority": "Medium",
                        "portion_size": None,
                    },
                    {
                        "ingredient_name": "spinach",
                        "quantity": 1.0,
                        "unit": "bunch",
                        "priority": "Urgent",
                        "portion_size": None,
                    },
                ]
            },
        )

        response = client.get("/api/inventory")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should have all expected fields
        assert "id" in data[0]
        assert "ingredient_name" in data[0]
        assert "quantity" in data[0]
        assert "unit" in data[0]
        assert "priority" in data[0]
        assert "portion_size" in data[0]
        assert "added_at" in data[0]

    def test_list_returns_empty_for_no_items(self, client, session):
        """List endpoint returns empty list when no inventory"""
        seed_defaults(session)

        response = client.get("/api/inventory")

        assert response.status_code == 200
        data = response.json()
        assert data == []
