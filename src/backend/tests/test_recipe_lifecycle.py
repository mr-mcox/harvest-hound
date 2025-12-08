"""
Tests for recipe lifecycle endpoints (cook, abandon)
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models import GroceryStore, IngredientClaim, InventoryItem, Recipe, RecipeState


def _create_store(session: Session) -> GroceryStore:
    """Helper to create a grocery store"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_inventory_item(
    session: Session, store: GroceryStore, name: str, quantity: float, unit: str
) -> InventoryItem:
    """Helper to create an inventory item"""
    item = InventoryItem(
        store_id=store.id,
        ingredient_name=name,
        quantity=quantity,
        unit=unit,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def _create_recipe_with_claim(
    session: Session, inventory_item: InventoryItem
) -> Recipe:
    """Helper to create a recipe with a claim on an inventory item"""
    recipe = Recipe(
        name="Test Recipe",
        description="A test recipe",
        ingredients=[
            {
                "name": inventory_item.ingredient_name,
                "quantity": "1",
                "unit": inventory_item.unit,
            }
        ],
        instructions=["Step 1", "Step 2"],
        active_time_minutes=15,
        total_time_minutes=30,
        servings=4,
        state=RecipeState.PLANNED,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    # Create claim
    claim = IngredientClaim(
        recipe_id=recipe.id,
        inventory_item_id=inventory_item.id,
        ingredient_name=inventory_item.ingredient_name,
        quantity=1.0,
        unit=inventory_item.unit,
    )
    session.add(claim)
    session.commit()

    return recipe


class TestCookEndpoint:
    """Tests for POST /recipes/{id}/cook endpoint"""

    def test_cook_recipe_transitions_state_and_deletes_claims(
        self, session: Session, client: TestClient
    ):
        """Happy path: cooking a recipe transitions state and deletes claims"""
        store = _create_store(session)
        item = _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        recipe = _create_recipe_with_claim(session, item)

        response = client.post(f"/api/recipes/{recipe.id}/cook")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe_id"] == str(recipe.id)
        assert data["new_state"] == "cooked"
        assert data["claims_deleted"] == 1
        assert data["inventory_items_decremented"] == 1

        # Verify recipe state changed
        session.expire_all()
        loaded_recipe = session.get(Recipe, recipe.id)
        assert loaded_recipe.state == RecipeState.COOKED
        assert loaded_recipe.cooked_at is not None

        # Verify claims deleted
        claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
        ).all()
        assert len(claims) == 0

        # Verify inventory decremented
        loaded_item = session.get(InventoryItem, item.id)
        assert loaded_item.quantity == 1.0  # 2.0 - 1.0

    def test_cook_recipe_is_idempotent(self, session: Session, client: TestClient):
        """Calling cook twice produces same result (no-op on second call)"""
        store = _create_store(session)
        item = _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        recipe = _create_recipe_with_claim(session, item)

        # First cook
        response1 = client.post(f"/api/recipes/{recipe.id}/cook")
        assert response1.status_code == 200

        # Second cook (should be no-op)
        response2 = client.post(f"/api/recipes/{recipe.id}/cook")
        assert response2.status_code == 200
        data = response2.json()
        assert data["new_state"] == "cooked"
        assert data["claims_deleted"] == 0  # Already deleted
        assert data["inventory_items_decremented"] == 0  # Already decremented

        # Verify inventory only decremented once
        session.expire_all()
        loaded_item = session.get(InventoryItem, item.id)
        assert loaded_item.quantity == 1.0  # Still 1.0, not 0.0

    def test_cook_recipe_not_found_returns_404(
        self, session: Session, client: TestClient
    ):
        """Cooking non-existent recipe returns 404"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.post(f"/api/recipes/{fake_id}/cook")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_cook_handles_deleted_inventory_gracefully(
        self, session: Session, client: TestClient
    ):
        """If inventory item deleted between planning and cooking, handle gracefully"""
        store = _create_store(session)
        item = _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        recipe = _create_recipe_with_claim(session, item)

        # Delete inventory item (simulating staleness)
        session.delete(item)
        session.commit()

        # Cook should still work, just skip inventory decrement
        response = client.post(f"/api/recipes/{recipe.id}/cook")

        assert response.status_code == 200
        data = response.json()
        assert data["new_state"] == "cooked"
        assert data["claims_deleted"] == 0  # Cascade delete already removed claims
        assert data["inventory_items_decremented"] == 0  # Item was deleted

    def test_cook_multiple_claims_decrements_all_inventory(
        self, session: Session, client: TestClient
    ):
        """Cooking recipe with multiple claims decrements all inventory items"""
        store = _create_store(session)
        item1 = _create_inventory_item(session, store, "carrots", 3.0, "pounds")
        item2 = _create_inventory_item(session, store, "onions", 5.0, "whole")

        recipe = Recipe(
            name="Soup",
            description="Veggie soup",
            ingredients=[
                {"name": "carrots", "quantity": "2", "unit": "pounds"},
                {"name": "onions", "quantity": "3", "unit": "whole"},
            ],
            instructions=["Cook"],
            active_time_minutes=30,
            total_time_minutes=60,
            servings=4,
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        # Create claims for both items
        claim1 = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item1.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        claim2 = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item2.id,
            ingredient_name="onions",
            quantity=3.0,
            unit="whole",
        )
        session.add(claim1)
        session.add(claim2)
        session.commit()

        response = client.post(f"/api/recipes/{recipe.id}/cook")

        assert response.status_code == 200
        data = response.json()
        assert data["claims_deleted"] == 2
        assert data["inventory_items_decremented"] == 2

        # Verify both items decremented
        session.expire_all()
        loaded_item1 = session.get(InventoryItem, item1.id)
        loaded_item2 = session.get(InventoryItem, item2.id)
        assert loaded_item1.quantity == 1.0  # 3.0 - 2.0
        assert loaded_item2.quantity == 2.0  # 5.0 - 3.0


class TestAbandonEndpoint:
    """Tests for POST /recipes/{id}/abandon endpoint"""

    def test_abandon_recipe_transitions_state_and_deletes_claims(
        self, session: Session, client: TestClient
    ):
        """Happy path: abandoning a recipe transitions state and deletes claims"""
        store = _create_store(session)
        item = _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        recipe = _create_recipe_with_claim(session, item)

        response = client.post(f"/api/recipes/{recipe.id}/abandon")

        assert response.status_code == 200
        data = response.json()
        assert data["recipe_id"] == str(recipe.id)
        assert data["new_state"] == "abandoned"
        assert data["claims_deleted"] == 1
        assert data["inventory_items_decremented"] == 0  # No inventory change

        # Verify recipe state changed
        session.expire_all()
        loaded_recipe = session.get(Recipe, recipe.id)
        assert loaded_recipe.state == RecipeState.ABANDONED
        assert loaded_recipe.cooked_at is None  # Not cooked

        # Verify claims deleted
        claims = session.exec(
            select(IngredientClaim).where(IngredientClaim.recipe_id == recipe.id)
        ).all()
        assert len(claims) == 0

        # Verify inventory NOT decremented
        loaded_item = session.get(InventoryItem, item.id)
        assert loaded_item.quantity == 2.0  # Still 2.0 (released back)

    def test_abandon_recipe_is_idempotent(self, session: Session, client: TestClient):
        """Calling abandon twice produces same result (no-op on second call)"""
        store = _create_store(session)
        item = _create_inventory_item(session, store, "carrots", 2.0, "pounds")
        recipe = _create_recipe_with_claim(session, item)

        # First abandon
        response1 = client.post(f"/api/recipes/{recipe.id}/abandon")
        assert response1.status_code == 200

        # Second abandon (should be no-op)
        response2 = client.post(f"/api/recipes/{recipe.id}/abandon")
        assert response2.status_code == 200
        data = response2.json()
        assert data["new_state"] == "abandoned"
        assert data["claims_deleted"] == 0  # Already deleted
        assert data["inventory_items_decremented"] == 0

    def test_abandon_recipe_not_found_returns_404(
        self, session: Session, client: TestClient
    ):
        """Abandoning non-existent recipe returns 404"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.post(f"/api/recipes/{fake_id}/abandon")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
