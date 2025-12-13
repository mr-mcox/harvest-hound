"""
Tests for inventory API endpoints (parse, bulk, list)
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import select

from models import InventoryItem, seed_defaults


@pytest.fixture(autouse=True)
def _seed_defaults(session):
    """Automatically seed defaults for all inventory API tests."""
    seed_defaults(session)


def _mock_ingredient(name, quantity, unit, priority, portion_size=None):
    """Create a mock ingredient with proper attribute access."""
    mock = MagicMock()
    mock.name = name
    mock.quantity = quantity
    mock.unit = unit
    mock.priority = priority
    mock.portion_size = portion_size
    return mock


# Common test items (use dict spreading for variations: {**CARROT, "quantity": 3.0})
CARROT = {
    "ingredient_name": "carrot",
    "quantity": 2.0,
    "unit": "pound",
    "priority": "Medium",
    "portion_size": None,
}

SPINACH = {
    "ingredient_name": "spinach",
    "quantity": 1.0,
    "unit": "bunch",
    "priority": "Urgent",
    "portion_size": None,
}

GROUND_BEEF = {
    "ingredient_name": "ground beef",
    "quantity": 3.0,
    "unit": "package",
    "priority": "High",
    "portion_size": "1 pound",
}


def _create_item_via_bulk(client, item=None):
    """Helper to create inventory item(s) via bulk endpoint. Defaults to CARROT."""
    if item is None:
        item = CARROT
    client.post("/api/inventory/bulk", json={"items": [item]})


def _create_inventory_item(session, item_dict=None, **overrides):
    """Create inventory item directly in DB and return it. Defaults to CARROT."""
    from models import GroceryStore

    if item_dict is None:
        item_dict = CARROT

    # Merge item_dict with overrides
    data = {**item_dict, **overrides}

    store = session.exec(select(GroceryStore)).first()
    item = InventoryItem(store_id=store.id, **data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


class TestInventoryParseAPI:
    """Tests for POST /api/inventory/parse endpoint"""

    def test_parse_returns_parsed_ingredients(self, client, session):
        """Parse endpoint calls BAML and returns parsed ingredients"""
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
        kale = {**SPINACH, "ingredient_name": "kale"}
        response = client.post("/api/inventory/bulk", json={"items": [CARROT, kale]})

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
        response = client.post("/api/inventory/bulk", json={"items": [GROUND_BEEF]})

        assert response.status_code == 200
        item = session.exec(select(InventoryItem)).first()
        assert item.portion_size == GROUND_BEEF["portion_size"]

    def test_bulk_empty_list_returns_zero(self, client, session):
        """Bulk endpoint handles empty list gracefully"""
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
        client.post("/api/inventory/bulk", json={"items": [CARROT, SPINACH]})

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
        response = client.get("/api/inventory")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_excludes_deleted_items(self, client, session):
        """List endpoint filters out soft-deleted items"""
        client.post("/api/inventory/bulk", json={"items": [CARROT, SPINACH]})

        # Get item IDs
        items = session.exec(select(InventoryItem)).all()
        assert len(items) == 2
        carrot_id = items[0].id

        # Soft delete the carrot
        response = client.delete(f"/api/inventory/{carrot_id}")
        assert response.status_code == 200

        # List should only return spinach
        response = client.get("/api/inventory")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ingredient_name"] == "spinach"


class TestInventoryDeleteAPI:
    """Tests for DELETE /api/inventory/{id} endpoint"""

    def test_delete_soft_deletes_item(self, client, session):
        """Delete endpoint sets deleted_at timestamp instead of removing row"""
        _create_item_via_bulk(client)
        item = session.exec(select(InventoryItem)).first()
        assert item is not None
        item_id = item.id

        # Delete the item
        response = client.delete(f"/api/inventory/{item_id}")
        assert response.status_code == 200

        # Item should still exist in database but have deleted_at set
        session.expire_all()
        deleted_item = session.get(InventoryItem, item_id)
        assert deleted_item is not None
        assert deleted_item.deleted_at is not None

    def test_delete_preserves_foreign_key_integrity_with_claims(self, client, session):
        """Soft delete preserves FK integrity - claims on deleted items still exist"""
        from models import GroceryStore, IngredientClaim, Recipe

        # Create inventory item
        store = session.exec(select(GroceryStore)).first()
        item = InventoryItem(
            store_id=store.id,
            ingredient_name="carrot",
            quantity=2.0,
            unit="pound",
            priority="medium",
        )
        session.add(item)
        session.commit()
        session.refresh(item)

        # Create recipe
        recipe = Recipe(
            name="Carrot Soup",
            description="Test recipe",
            ingredients=[{"name": "carrot", "quantity": "2", "unit": "pound"}],
            instructions=["Cook"],
            active_time_minutes=10,
            total_time_minutes=30,
            servings=2,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        # Create claim
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item.id,
            ingredient_name="carrot",
            quantity=2.0,
            unit="pound",
        )
        session.add(claim)
        session.commit()
        claim_id = claim.id

        # Soft delete the inventory item
        response = client.delete(f"/api/inventory/{item.id}")
        assert response.status_code == 200

        # Claim should still exist
        session.expire_all()
        persisted_claim = session.get(IngredientClaim, claim_id)
        assert persisted_claim is not None
        assert persisted_claim.inventory_item_id == item.id

    def test_delete_nonexistent_item_returns_404(self, client, session):
        """Delete endpoint returns 404 for nonexistent item"""
        response = client.delete("/api/inventory/99999")
        assert response.status_code == 404


class TestInventoryUpdateAPI:
    """Tests for PATCH /api/inventory/{id} endpoint"""

    @pytest.fixture
    def carrot_item_id(self, client, session):
        """Create a standard carrot item and return its ID."""
        _create_item_via_bulk(client)
        item = session.exec(select(InventoryItem)).first()
        return item.id

    def test_update_quantity_only(self, client, carrot_item_id):
        """PATCH endpoint updates only quantity, priority unchanged"""
        response = client.patch(
            f"/api/inventory/{carrot_item_id}",
            json={"quantity": 1.5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1.5
        assert data["priority"] == CARROT["priority"]  # Unchanged

    def test_update_priority_only(self, client, carrot_item_id):
        """PATCH endpoint updates only priority, quantity unchanged"""
        response = client.patch(
            f"/api/inventory/{carrot_item_id}",
            json={"priority": "Urgent"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == CARROT["quantity"]  # Unchanged
        assert data["priority"] == "Urgent"

    def test_update_both_quantity_and_priority(self, client, carrot_item_id):
        """PATCH endpoint updates both quantity and priority"""
        response = client.patch(
            f"/api/inventory/{carrot_item_id}",
            json={"quantity": 3.5, "priority": "High"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 3.5
        assert data["priority"] == "High"

    def test_update_rejects_zero_quantity(self, client, carrot_item_id):
        """PATCH endpoint rejects quantity of 0"""
        response = client.patch(
            f"/api/inventory/{carrot_item_id}",
            json={"quantity": 0.0},
        )

        assert response.status_code == 400

    def test_update_rejects_negative_quantity(self, client, carrot_item_id):
        """PATCH endpoint rejects negative quantity"""
        response = client.patch(
            f"/api/inventory/{carrot_item_id}",
            json={"quantity": -1.0},
        )

        assert response.status_code == 400

    def test_update_nonexistent_item_returns_404(self, client, session):
        """PATCH endpoint returns 404 for nonexistent item"""
        response = client.patch(
            "/api/inventory/99999",
            json={"quantity": 5.0},
        )

        assert response.status_code == 404


class TestInventoryWithClaimsAPI:
    """Tests for GET /api/inventory/with-claims endpoint"""

    def test_unclaimed_item_shows_full_availability(self, client, session):
        """Inventory item with no claims shows available = quantity"""
        _create_item_via_bulk(client, CARROT)

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        item = data[0]
        assert item["ingredient_name"] == CARROT["ingredient_name"]
        assert item["quantity"] == CARROT["quantity"]
        assert item["available"] == CARROT["quantity"]  # No claims, fully available
        assert item["claims"] == []

    def test_partially_claimed_item_shows_reduced_availability(self, client, session):
        """Inventory item with claims shows available = quantity - reserved"""
        from models import IngredientClaim, Recipe

        # Create inventory item with 5 pounds
        inventory_item = _create_inventory_item(session, quantity=5.0)
        claimed_qty = 2.0

        # Create recipe claiming 2 pounds
        recipe = Recipe(
            name="Carrot Soup",
            description="Delicious soup",
            ingredients=[{"name": "carrot", "quantity": "2", "unit": "pound"}],
            instructions=["Cook"],
            active_time_minutes=10,
            total_time_minutes=30,
            servings=2,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        # Create claim
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claimed_qty,
            unit="pound",
        )
        session.add(claim)
        session.commit()

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        assert result["ingredient_name"] == inventory_item.ingredient_name
        assert result["quantity"] == inventory_item.quantity
        assert result["available"] == inventory_item.quantity - claimed_qty
        assert len(result["claims"]) == 1
        assert result["claims"][0]["recipe_name"] == recipe.name
        assert result["claims"][0]["quantity"] == claimed_qty
        assert result["claims"][0]["unit"] == inventory_item.unit

    def test_fully_claimed_item_shows_zero_availability(self, client, session):
        """Inventory item fully claimed shows available = 0"""
        from models import IngredientClaim, Recipe

        # Create inventory item (CARROT defaults to 2.0 pounds)
        inventory_item = _create_inventory_item(session)
        claimed_qty = inventory_item.quantity  # Claim all of it

        # Create recipe claiming all quantity
        recipe = Recipe(
            name="Carrot Cake",
            description="Sweet cake",
            ingredients=[{"name": "carrot", "quantity": "2", "unit": "pound"}],
            instructions=["Bake"],
            active_time_minutes=20,
            total_time_minutes=60,
            servings=8,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        # Create claim for full quantity
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claimed_qty,
            unit="pound",
        )
        session.add(claim)
        session.commit()

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        assert result["quantity"] == inventory_item.quantity
        assert result["available"] == 0.0  # Fully claimed
        assert len(result["claims"]) == 1

    def test_multiple_recipes_claiming_same_ingredient(self, client, session):
        """Multiple recipes claiming same ingredient aggregates correctly"""
        from models import IngredientClaim, Recipe

        # Create inventory item with 10 pounds
        inventory_item = _create_inventory_item(session, quantity=10.0)
        claim1_qty = 3.0
        claim2_qty = 4.0

        # Create first recipe claiming 3 pounds
        recipe1 = Recipe(
            name="Carrot Soup",
            description="Soup",
            ingredients=[{"name": "carrot", "quantity": "3", "unit": "pound"}],
            instructions=["Cook"],
            active_time_minutes=10,
            total_time_minutes=30,
            servings=2,
        )
        session.add(recipe1)
        session.commit()
        session.refresh(recipe1)

        claim1 = IngredientClaim(
            recipe_id=recipe1.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claim1_qty,
            unit="pound",
        )
        session.add(claim1)

        # Create second recipe claiming 4 pounds
        recipe2 = Recipe(
            name="Carrot Cake",
            description="Cake",
            ingredients=[{"name": "carrot", "quantity": "4", "unit": "pound"}],
            instructions=["Bake"],
            active_time_minutes=20,
            total_time_minutes=60,
            servings=8,
        )
        session.add(recipe2)
        session.commit()
        session.refresh(recipe2)

        claim2 = IngredientClaim(
            recipe_id=recipe2.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claim2_qty,
            unit="pound",
        )
        session.add(claim2)
        session.commit()

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        total_claimed = claim1_qty + claim2_qty
        assert result["quantity"] == inventory_item.quantity
        assert result["available"] == inventory_item.quantity - total_claimed
        assert len(result["claims"]) == 2
        # Verify both recipes are in claims
        recipe_names = {claim["recipe_name"] for claim in result["claims"]}
        assert recipe_names == {recipe1.name, recipe2.name}

    def test_all_returned_claims_are_reserved(self, client, session):
        """Endpoint only returns RESERVED claims (others are deleted)"""
        from models import ClaimState, IngredientClaim, Recipe

        # Create inventory item with 10 pounds
        inventory_item = _create_inventory_item(session, quantity=10.0)
        claimed_qty = 2.0

        # Create recipe with RESERVED claim
        recipe = Recipe(
            name="Carrot Soup",
            description="Soup",
            ingredients=[{"name": "carrot", "quantity": "2", "unit": "pound"}],
            instructions=["Cook"],
            active_time_minutes=10,
            total_time_minutes=30,
            servings=2,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claimed_qty,
            unit="pound",
            state=ClaimState.RESERVED,
        )
        session.add(claim)
        session.commit()

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        assert result["available"] == inventory_item.quantity - claimed_qty
        assert len(result["claims"]) == 1
        assert result["claims"][0]["recipe_name"] == recipe.name

    def test_empty_inventory_returns_empty_list(self, client, session):
        """Endpoint returns empty list when no inventory exists"""
        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_excludes_soft_deleted_items(self, client, session):
        """Endpoint excludes soft-deleted inventory items"""
        _create_item_via_bulk(client, CARROT)
        _create_item_via_bulk(client, SPINACH)

        # Get item IDs
        items = session.exec(select(InventoryItem)).all()
        carrot_id = items[0].id

        # Soft delete the carrot
        client.delete(f"/api/inventory/{carrot_id}")

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        assert result["ingredient_name"] == SPINACH["ingredient_name"]

    def test_over_claimed_item_shows_zero_not_negative(self, client, session):
        """Inventory item claimed beyond physical quantity shows 0, not negative"""
        from models import IngredientClaim, Recipe

        # Create inventory item (CARROT defaults to 2.0 pounds)
        inventory_item = _create_inventory_item(session)
        claimed_qty = 5.0  # More than available

        # Create recipe claiming more than available
        recipe = Recipe(
            name="Carrot Soup",
            description="Soup",
            ingredients=[{"name": "carrot", "quantity": "5", "unit": "pound"}],
            instructions=["Cook"],
            active_time_minutes=10,
            total_time_minutes=30,
            servings=4,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrot",
            quantity=claimed_qty,
            unit="pound",
        )
        session.add(claim)
        session.commit()

        response = client.get("/api/inventory/with-claims")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        result = data[0]
        assert result["quantity"] == inventory_item.quantity
        assert result["available"] == 0.0  # Should be 0, not negative
