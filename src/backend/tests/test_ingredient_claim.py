"""
Tests for IngredientClaim behavior - tracking inventory reservations for recipes
"""

from sqlmodel import Session

from models import (
    ClaimState,
    GroceryStore,
    IngredientClaim,
    InventoryItem,
    Recipe,
)


def _create_grocery_store(session: Session) -> GroceryStore:
    """Helper to create a grocery store for inventory items"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_inventory_item(session: Session, store: GroceryStore) -> InventoryItem:
    """Helper to create an inventory item"""
    item = InventoryItem(
        store_id=store.id,
        ingredient_name="carrots",
        quantity=2.0,
        unit="pounds",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def _create_recipe(session: Session) -> Recipe:
    """Helper to create a recipe"""
    recipe = Recipe(
        name="Carrot Soup",
        description="Warming soup",
        ingredients=[{"name": "carrots", "quantity": "2", "unit": "pounds"}],
        instructions=["Cook carrots", "Blend"],
        active_time_minutes=15,
        total_time_minutes=45,
        servings=4,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


class TestIngredientClaimBehavior:
    """Tests for IngredientClaim linking recipes to inventory items"""

    def test_can_create_claim_linking_recipe_to_inventory_item(self, session: Session):
        """Happy path: claim reserves inventory for a recipe"""
        store = _create_grocery_store(session)
        item = _create_inventory_item(session, store)
        recipe = _create_recipe(session)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        session.add(claim)
        session.commit()

        # Verify claim exists and links correctly
        session.expire_all()
        loaded = session.get(IngredientClaim, claim.id)

        assert loaded is not None
        assert loaded.recipe_id == recipe.id
        assert loaded.inventory_item_id == item.id
        assert loaded.ingredient_name == "carrots"
        assert loaded.quantity == 2.0
        assert loaded.state == ClaimState.RESERVED  # Default state

    def test_deleting_recipe_cascades_to_claims(self, session: Session):
        """When recipe is deleted, its claims are also deleted"""
        store = _create_grocery_store(session)
        item = _create_inventory_item(session, store)
        recipe = _create_recipe(session)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        session.add(claim)
        session.commit()
        claim_id = claim.id

        session.delete(recipe)
        session.commit()

        assert session.get(IngredientClaim, claim_id) is None

    def test_deleting_inventory_item_cascades_to_claims(self, session: Session):
        """When inventory item is deleted, claims referencing it are also deleted"""
        store = _create_grocery_store(session)
        item = _create_inventory_item(session, store)
        recipe = _create_recipe(session)

        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=item.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        session.add(claim)
        session.commit()
        claim_id = claim.id

        session.delete(item)
        session.commit()

        assert session.get(IngredientClaim, claim_id) is None
