"""
Tests for shopping list computation algorithm
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from models import (
    GroceryStore,
    IngredientClaim,
    InventoryItem,
    PlanningSession,
    Recipe,
    RecipeState,
    ShoppingListSelection,
)
from shopping_list import compute_shopping_list


def _create_session(session: Session) -> PlanningSession:
    """Helper to create a planning session"""
    planning_session = PlanningSession(name="Weekly Meal Plan")
    session.add(planning_session)
    session.commit()
    session.refresh(planning_session)
    return planning_session


def _create_store(session: Session) -> GroceryStore:
    """Helper to create a grocery store"""
    store = GroceryStore(name="CSA Box", description="Weekly delivery")
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _create_recipe(
    session: Session,
    planning_session: PlanningSession,
    name: str,
    ingredients: list[dict],
) -> Recipe:
    """Helper to create a recipe with ingredients"""
    recipe = Recipe(
        name=name,
        description=f"{name} description",
        ingredients=ingredients,
        instructions=["Step 1"],
        active_time_minutes=30,
        total_time_minutes=60,
        servings=4,
        state=RecipeState.PLANNED,
        session_id=planning_session.id,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


class TestShoppingListComputation:
    """Tests for shopping list computation algorithm"""

    def test_empty_session_returns_empty_list(self, session: Session):
        """No recipes means empty shopping list"""
        planning_session = _create_session(session)

        result = compute_shopping_list(session, planning_session.id)

        assert result.grocery_items == []
        assert result.pantry_staples == []

    def test_single_recipe_single_grocery_item(self, session: Session):
        """Single recipe with one grocery item appears on list"""
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Pasta",
            [
                {
                    "name": "pasta",
                    "quantity": "1",
                    "unit": "pound",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "pasta"
        assert result.grocery_items[0].total_quantity == "1 pound"
        assert result.grocery_items[0].purchase_likelihood == 0.8
        assert result.grocery_items[0].used_in_recipes == ["Pasta"]

    def test_pantry_staples_filtered_out(self, session: Session):
        """Ingredients with likelihood < 0.3 don't appear on grocery list"""
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "lettuce",
                    "quantity": "1",
                    "unit": "head",
                    "purchase_likelihood": 0.9,  # Grocery
                },
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "tsp",
                    "purchase_likelihood": 0.1,  # Pantry staple
                },
                {
                    "name": "olive oil",
                    "quantity": "2",
                    "unit": "tbsp",
                    "purchase_likelihood": 0.2,  # Pantry staple
                },
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Only lettuce on grocery list
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "lettuce"

        # Pantry staples appear in separate section
        assert len(result.pantry_staples) == 2
        pantry_names = {item.ingredient_name for item in result.pantry_staples}
        assert pantry_names == {"salt", "olive oil"}

    def test_claimed_ingredients_excluded(self, session: Session):
        """Ingredients with claims (from inventory) don't appear on list"""
        planning_session = _create_session(session)
        store = _create_store(session)

        # Create inventory item
        inventory_item = InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=5.0,
            unit="pounds",
        )
        session.add(inventory_item)
        session.commit()
        session.refresh(inventory_item)

        # Create recipe with carrots
        recipe = _create_recipe(
            session,
            planning_session,
            "Soup",
            [
                {
                    "name": "carrots",
                    "quantity": "2",
                    "unit": "pounds",
                    "purchase_likelihood": 0.7,
                },
                {
                    "name": "onions",
                    "quantity": "3",
                    "unit": "whole",
                    "purchase_likelihood": 0.6,
                },
            ],
        )

        # Create claim for carrots (from inventory)
        claim = IngredientClaim(
            recipe_id=recipe.id,
            inventory_item_id=inventory_item.id,
            ingredient_name="carrots",
            quantity=2.0,
            unit="pounds",
        )
        session.add(claim)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        # Only onions on list (carrots claimed from inventory)
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "onions"

    def test_aggregate_same_ingredient_across_recipes(self, session: Session):
        """Same ingredient in multiple recipes gets aggregated"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Pasta",
            [
                {
                    "name": "tomatoes",
                    "quantity": "2",
                    "unit": "cups",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "tomatoes",
                    "quantity": "1",
                    "unit": "whole",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Single aggregated entry for tomatoes
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "tomatoes"
        assert result.grocery_items[0].total_quantity == "2 cups + 1 whole"
        assert result.grocery_items[0].used_in_recipes == ["Pasta", "Salad"]

    def test_grocery_items_sorted_by_likelihood_desc(self, session: Session):
        """Grocery items sorted by purchase_likelihood descending"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Mixed",
            [
                {
                    "name": "item_low",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.4,
                },
                {
                    "name": "item_high",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.9,
                },
                {
                    "name": "item_mid",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.6,
                },
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be sorted: high (0.9), mid (0.6), low (0.4)
        assert len(result.grocery_items) == 3
        assert result.grocery_items[0].ingredient_name == "item_high"
        assert result.grocery_items[1].ingredient_name == "item_mid"
        assert result.grocery_items[2].ingredient_name == "item_low"

    def test_only_planned_recipes_included(self, session: Session):
        """Only recipes in PLANNED state appear on shopping list"""
        planning_session = _create_session(session)

        # Planned recipe
        _create_recipe(
            session,
            planning_session,
            "Planned",
            [
                {
                    "name": "item1",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        # Cooked recipe (should be excluded)
        cooked_recipe = _create_recipe(
            session,
            planning_session,
            "Cooked",
            [
                {
                    "name": "item2",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.8,
                }
            ],
        )
        cooked_recipe.state = RecipeState.COOKED
        session.add(cooked_recipe)
        session.commit()

        result = compute_shopping_list(session, planning_session.id)

        # Only item1 from planned recipe
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "item1"

    def test_threshold_exactly_0_3_is_grocery(self, session: Session):
        """Ingredient with likelihood exactly 0.3 is grocery (boundary test)"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Boundary",
            [
                {
                    "name": "boundary_item",
                    "quantity": "1",
                    "unit": "unit",
                    "purchase_likelihood": 0.3,  # Exactly at threshold
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be on grocery list (≥0.3)
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "boundary_item"
        assert len(result.pantry_staples) == 0

    def test_aggregate_same_unit_sums_quantities(self, session: Session):
        """Same ingredient with same unit should sum numeric quantities"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "garlic",
                    "quantity": "6",
                    "unit": "clove",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 2",
            [
                {
                    "name": "garlic",
                    "quantity": "4",
                    "unit": "clove",
                    "purchase_likelihood": 0.7,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should sum to 10 clove (or cloves)
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "garlic"
        # Accept either "10 clove" or "10 cloves" - pluralization can go either way
        assert result.grocery_items[0].total_quantity in ["10 clove", "10 cloves"]
        assert result.grocery_items[0].used_in_recipes == ["Recipe 1", "Recipe 2"]

    def test_aggregate_normalizes_plural_units(self, session: Session):
        """Ingredient with 'clove' and 'cloves' should be treated as same unit"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "garlic",
                    "quantity": "6",
                    "unit": "clove",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 2",
            [
                {
                    "name": "garlic",
                    "quantity": "4",
                    "unit": "clove",
                    "purchase_likelihood": 0.7,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 3",
            [
                {
                    "name": "garlic",
                    "quantity": "6",
                    "unit": "cloves",  # Plural
                    "purchase_likelihood": 0.9,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 4",
            [
                {
                    "name": "garlic",
                    "quantity": "6",
                    "unit": "cloves",  # Plural
                    "purchase_likelihood": 0.85,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should aggregate all garlic regardless of clove/cloves
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].ingredient_name == "garlic"
        # Should sum to 22 (6+4+6+6)
        assert result.grocery_items[0].total_quantity in ["22 clove", "22 cloves"]
        assert len(result.grocery_items[0].used_in_recipes) == 4

    def test_aggregate_non_numeric_quantities_concatenated(self, session: Session):
        """Non-numeric quantities like 'to taste' should be concatenated, not summed"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "salt",
                    "quantity": "to taste",
                    "unit": "pinch",
                    "purchase_likelihood": 0.1,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 2",
            [
                {
                    "name": "salt",
                    "quantity": "to taste",
                    "unit": "pinch",
                    "purchase_likelihood": 0.2,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Non-numeric should still concatenate
        assert len(result.pantry_staples) == 1
        assert result.pantry_staples[0].ingredient_name == "salt"
        assert (
            result.pantry_staples[0].total_quantity == "to taste pinch + to taste pinch"
        )

    def test_aggregate_mixed_numeric_and_non_numeric(self, session: Session):
        """Mix of numeric and non-numeric quantities should concatenate"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "pepper",
                    "quantity": "2",
                    "unit": "tsp",
                    "purchase_likelihood": 0.2,
                }
            ],
        )

        _create_recipe(
            session,
            planning_session,
            "Recipe 2",
            [
                {
                    "name": "pepper",
                    "quantity": "to taste",
                    "unit": "tsp",
                    "purchase_likelihood": 0.15,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Can't sum when one is non-numeric, so concatenate
        assert len(result.pantry_staples) == 1
        assert result.pantry_staples[0].ingredient_name == "pepper"
        assert result.pantry_staples[0].total_quantity == "2 tsp + to taste tsp"

    def test_aggregate_non_pluralizing_units(self, session: Session):
        """Units like 'each' should not be pluralized"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "shallots",
                    "quantity": "3",
                    "unit": "each",
                    "purchase_likelihood": 0.8,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be "3 each", not "3 eachs"
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].total_quantity == "3 each"

    def test_aggregate_size_descriptor_units(self, session: Session):
        """Size descriptors like 'medium' should not be pluralized"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Recipe 1",
            [
                {
                    "name": "shallot",
                    "quantity": "2",
                    "unit": "medium",
                    "purchase_likelihood": 0.9,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should be "2 medium", not "2 mediums"
        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].total_quantity == "2 medium"


class TestShoppingListAPIEndpoint:
    """Tests for GET /sessions/{session_id}/shopping-list API endpoint"""

    def test_get_shopping_list_returns_correct_structure(
        self, session: Session, client: TestClient
    ):
        """Happy path: endpoint returns shopping list with correct structure"""
        planning_session = _create_session(session)

        # Create recipe with mixed grocery/pantry items
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "lettuce",
                    "quantity": "1",
                    "unit": "head",
                    "purchase_likelihood": 0.9,
                },
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "tsp",
                    "purchase_likelihood": 0.1,
                },
            ],
        )

        # Call endpoint
        response = client.get(f"/api/sessions/{planning_session.id}/shopping-list")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "grocery_items" in data
        assert "pantry_staples" in data
        assert isinstance(data["grocery_items"], list)
        assert isinstance(data["pantry_staples"], list)

        # Check content
        assert len(data["grocery_items"]) == 1
        assert data["grocery_items"][0]["ingredient_name"] == "lettuce"
        assert data["grocery_items"][0]["total_quantity"] == "1 head"
        assert data["grocery_items"][0]["purchase_likelihood"] == 0.9
        assert data["grocery_items"][0]["used_in_recipes"] == ["Salad"]

        assert len(data["pantry_staples"]) == 1
        assert data["pantry_staples"][0]["ingredient_name"] == "salt"

    def test_get_shopping_list_empty_session_returns_empty_lists(
        self, session: Session, client: TestClient
    ):
        """Empty session returns empty grocery and pantry lists"""
        planning_session = _create_session(session)

        response = client.get(f"/api/sessions/{planning_session.id}/shopping-list")

        assert response.status_code == 200
        data = response.json()
        assert data["grocery_items"] == []
        assert data["pantry_staples"] == []

    def test_get_shopping_list_session_not_found_returns_404(self, client: TestClient):
        """Non-existent session returns 404"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.get(f"/api/sessions/{fake_id}/shopping-list")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestBayesianUpdate:
    """Tests for bayesian_update() function - Bayesian likelihood refinement"""

    def test_no_historical_data_returns_prior(self):
        """With zero sessions observed, return the LLM prior unchanged"""
        from shopping_list import bayesian_update

        prior = 0.8
        result = bayesian_update(prior=prior, sessions_observed=0, times_purchased=0)

        assert result == prior

    def test_sparse_data_favors_prior(self):
        """With few sessions (n < 5), prior is weighted heavily"""
        from shopping_list import bayesian_update

        # Onions: LLM says 0.8, but purchased 1/2 times (50% empirical)
        # With only 2 sessions, should still favor the prior
        result = bayesian_update(prior=0.8, sessions_observed=2, times_purchased=1)

        # Should be closer to 0.8 than to 0.5
        assert result > 0.6
        assert result < 0.8

    def test_substantial_data_shifts_toward_evidence(self):
        """With many sessions (n >= 10), evidence dominates"""
        from shopping_list import bayesian_update

        # Onions: LLM says 0.8, but skipped 10/11 times (only 1 purchase = 9% empirical)
        # Posterior should drop significantly from prior
        result = bayesian_update(prior=0.8, sessions_observed=11, times_purchased=1)

        # Should be much closer to empirical (0.09) than prior (0.8)
        # With 11 sessions, evidence weight is 11, prior weight is 5
        # posterior = (0.8 * 5 + 0.09 * 11) / 16 ≈ 0.31
        assert result < 0.35
        assert result < 0.8 / 2  # Less than half the prior

    def test_high_purchase_rate_increases_likelihood(self):
        """Ingredient purchased consistently should increase likelihood"""
        from shopping_list import bayesian_update

        # Goat cheese: LLM says 0.3 (pantry), but purchased 8/8 times
        # From TIP acceptance criteria: posterior should rise to ~0.9
        result = bayesian_update(prior=0.3, sessions_observed=8, times_purchased=8)

        assert result > 0.7  # Significantly shifted toward evidence

    def test_moderate_data_blends_prior_and_evidence(self):
        """With moderate sessions (5-9), blend prior and evidence"""
        from shopping_list import bayesian_update

        # 5 sessions, 3 purchases (60% empirical), prior 0.5
        result = bayesian_update(prior=0.5, sessions_observed=5, times_purchased=3)

        # Should be close to 0.5-0.6 range (balanced blend)
        assert 0.45 < result < 0.65

    def test_result_bounded_between_0_and_1(self):
        """Result is always a valid probability"""
        from shopping_list import bayesian_update

        # Edge case: all purchased
        result1 = bayesian_update(prior=0.1, sessions_observed=100, times_purchased=100)
        assert 0.0 <= result1 <= 1.0

        # Edge case: none purchased
        result2 = bayesian_update(prior=0.9, sessions_observed=100, times_purchased=0)
        assert 0.0 <= result2 <= 1.0

    def test_prior_zero_with_purchases_increases(self):
        """Even with prior=0, purchases should increase likelihood"""
        from shopping_list import bayesian_update

        result = bayesian_update(prior=0.0, sessions_observed=10, times_purchased=10)

        assert result > 0.5  # Should shift significantly toward evidence

    def test_prior_one_with_skips_decreases(self):
        """Even with prior=1, skips should decrease likelihood"""
        from shopping_list import bayesian_update

        result = bayesian_update(prior=1.0, sessions_observed=10, times_purchased=0)

        assert result < 0.5  # Should shift significantly toward evidence


class TestGetIngredientStats:
    """Tests for get_ingredient_stats() - deriving stats from reviewed selections"""

    def test_no_reviewed_selections_returns_empty_dict(self, session: Session):
        """With no reviewed selections, returns empty stats"""
        from shopping_list import get_ingredient_stats

        result = get_ingredient_stats(session)

        assert result == {}

    def test_unreviewed_selections_not_included(self, session: Session):
        """Selections without reviewed_at are excluded from stats"""
        from shopping_list import get_ingredient_stats

        planning_session = _create_session(session)

        # Create selection without reviewed_at (not reviewed)
        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="tomatoes",
            checked=True,
            reviewed_at=None,  # Not reviewed
        )
        session.add(selection)
        session.commit()

        result = get_ingredient_stats(session)

        assert result == {}

    def test_single_reviewed_session_counts_correctly(self, session: Session):
        """Single reviewed session with checked item shows 1 purchase"""
        from datetime import UTC, datetime

        from shopping_list import get_ingredient_stats

        planning_session = _create_session(session)

        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="tomatoes",
            checked=True,
            reviewed_at=datetime.now(UTC),
        )
        session.add(selection)
        session.commit()

        result = get_ingredient_stats(session)

        assert "tomatoes" in result
        assert result["tomatoes"]["sessions_observed"] == 1
        assert result["tomatoes"]["times_purchased"] == 1

    def test_single_reviewed_session_skipped_item(self, session: Session):
        """Reviewed session with unchecked item shows 0 purchases, 1 observed"""
        from datetime import UTC, datetime

        from shopping_list import get_ingredient_stats

        planning_session = _create_session(session)

        selection = ShoppingListSelection(
            session_id=planning_session.id,
            ingredient_name="onions",
            checked=False,  # Skipped
            reviewed_at=datetime.now(UTC),
        )
        session.add(selection)
        session.commit()

        result = get_ingredient_stats(session)

        assert "onions" in result
        assert result["onions"]["sessions_observed"] == 1
        assert result["onions"]["times_purchased"] == 0

    def test_multiple_sessions_aggregate_correctly(self, session: Session):
        """Stats aggregate across multiple reviewed sessions"""
        from datetime import UTC, datetime

        from shopping_list import get_ingredient_stats

        session1 = _create_session(session)
        session2 = _create_session(session)
        session3 = _create_session(session)

        # Garlic: purchased in 2/3 sessions
        selections = [
            ShoppingListSelection(
                session_id=session1.id,
                ingredient_name="garlic",
                checked=True,
                reviewed_at=datetime.now(UTC),
            ),
            ShoppingListSelection(
                session_id=session2.id,
                ingredient_name="garlic",
                checked=True,
                reviewed_at=datetime.now(UTC),
            ),
            ShoppingListSelection(
                session_id=session3.id,
                ingredient_name="garlic",
                checked=False,  # Skipped
                reviewed_at=datetime.now(UTC),
            ),
        ]
        for s in selections:
            session.add(s)
        session.commit()

        result = get_ingredient_stats(session)

        assert result["garlic"]["sessions_observed"] == 3
        assert result["garlic"]["times_purchased"] == 2

    def test_case_insensitive_ingredient_matching(self, session: Session):
        """Stats aggregate case-insensitively (Tomatoes == tomatoes)"""
        from datetime import UTC, datetime

        from shopping_list import get_ingredient_stats

        session1 = _create_session(session)
        session2 = _create_session(session)

        selections = [
            ShoppingListSelection(
                session_id=session1.id,
                ingredient_name="Tomatoes",  # Capitalized
                checked=True,
                reviewed_at=datetime.now(UTC),
            ),
            ShoppingListSelection(
                session_id=session2.id,
                ingredient_name="tomatoes",  # Lowercase
                checked=True,
                reviewed_at=datetime.now(UTC),
            ),
        ]
        for s in selections:
            session.add(s)
        session.commit()

        result = get_ingredient_stats(session)

        # Should be aggregated under lowercase key
        assert "tomatoes" in result
        assert result["tomatoes"]["sessions_observed"] == 2
        assert result["tomatoes"]["times_purchased"] == 2

    def test_multiple_ingredients_tracked_separately(self, session: Session):
        """Different ingredients have separate stats"""
        from datetime import UTC, datetime

        from shopping_list import get_ingredient_stats

        planning_session = _create_session(session)

        selections = [
            ShoppingListSelection(
                session_id=planning_session.id,
                ingredient_name="carrots",
                checked=True,
                reviewed_at=datetime.now(UTC),
            ),
            ShoppingListSelection(
                session_id=planning_session.id,
                ingredient_name="celery",
                checked=False,
                reviewed_at=datetime.now(UTC),
            ),
        ]
        for s in selections:
            session.add(s)
        session.commit()

        result = get_ingredient_stats(session)

        assert result["carrots"]["times_purchased"] == 1
        assert result["celery"]["times_purchased"] == 0


class TestBayesianRefinementIntegration:
    """Tests for Bayesian refinement in compute_shopping_list()"""

    def test_no_historical_data_uses_llm_prior(self, session: Session):
        """Without historical data, uses original LLM purchase_likelihood"""
        planning_session = _create_session(session)

        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "lettuce",
                    "quantity": "1",
                    "unit": "head",
                    "purchase_likelihood": 0.9,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.grocery_items) == 1
        assert result.grocery_items[0].purchase_likelihood == 0.9

    def test_historical_data_refines_likelihood_downward(self, session: Session):
        """Ingredient frequently skipped should have lower likelihood"""
        from datetime import UTC, datetime

        # Create historical data: onions skipped in 10 prior sessions
        for i in range(10):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="onions",
                checked=False,  # Skipped
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)
        session.commit()

        # Create current session with recipe using onions
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Soup",
            [
                {
                    "name": "onions",
                    "quantity": "2",
                    "unit": "whole",
                    "purchase_likelihood": 0.8,  # LLM says likely to buy
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # With 10 sessions of 0 purchases, likelihood drops significantly
        # 0.8 prior with 0/10 empirical → refined to ~0.27 (below 0.3 threshold)
        # So onions move from grocery to pantry
        assert len(result.pantry_staples) == 1
        assert result.pantry_staples[0].ingredient_name == "onions"
        assert result.pantry_staples[0].purchase_likelihood < 0.3

    def test_historical_data_refines_likelihood_upward(self, session: Session):
        """Ingredient frequently purchased should have higher likelihood"""
        from datetime import UTC, datetime

        # Create historical data: goat cheese purchased in 8 prior sessions
        for i in range(8):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="goat cheese",
                checked=True,  # Purchased
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)
        session.commit()

        # Create current session with recipe using goat cheese
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "goat cheese",
                    "quantity": "4",
                    "unit": "oz",
                    "purchase_likelihood": 0.3,  # LLM says borderline pantry
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        assert len(result.grocery_items) == 1
        # Should be refined upward from 0.3 due to historical purchases
        assert result.grocery_items[0].purchase_likelihood > 0.6

    def test_refined_likelihood_affects_grocery_pantry_split(self, session: Session):
        """Refinement can move item from grocery to pantry (or vice versa)"""
        from datetime import UTC, datetime

        # Create historical data: salt always skipped (11 sessions)
        for i in range(11):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="salt",
                checked=False,
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)
        session.commit()

        # Create current session with salt at 0.4 (would be grocery without refinement)
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Pasta",
            [
                {
                    "name": "salt",
                    "quantity": "1",
                    "unit": "tsp",
                    "purchase_likelihood": 0.4,  # Above 0.3 threshold = grocery
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # After refinement with 0/11 purchases, should drop below 0.3 → pantry
        assert len(result.grocery_items) == 0
        assert len(result.pantry_staples) == 1
        assert result.pantry_staples[0].ingredient_name == "salt"

    def test_case_insensitive_stats_matching(self, session: Session):
        """Stats for 'Tomatoes' apply to 'tomatoes' in recipe"""
        from datetime import UTC, datetime

        # Historical data uses "Tomatoes" (capitalized)
        for i in range(10):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="Tomatoes",
                checked=True,
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)
        session.commit()

        # Recipe uses "tomatoes" (lowercase)
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Salad",
            [
                {
                    "name": "tomatoes",
                    "quantity": "2",
                    "unit": "whole",
                    "purchase_likelihood": 0.5,
                }
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Should apply stats and refine upward (10/10 purchases)
        assert result.grocery_items[0].purchase_likelihood > 0.7

    def test_refined_likelihood_affects_sort_order(self, session: Session):
        """Grocery items sorted by refined likelihood, not LLM prior"""
        from datetime import UTC, datetime

        # Historical: carrots always purchased (high confidence)
        for i in range(10):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="carrots",
                checked=True,
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)

        # Historical: celery always skipped (low confidence)
        for i in range(10):
            old_session = _create_session(session)
            selection = ShoppingListSelection(
                session_id=old_session.id,
                ingredient_name="celery",
                checked=False,
                reviewed_at=datetime.now(UTC),
            )
            session.add(selection)
        session.commit()

        # Recipe: celery has higher LLM prior, but historical says otherwise
        planning_session = _create_session(session)
        _create_recipe(
            session,
            planning_session,
            "Soup",
            [
                {
                    "name": "carrots",
                    "quantity": "3",
                    "unit": "whole",
                    "purchase_likelihood": 0.5,  # LLM: lower
                },
                {
                    "name": "celery",
                    "quantity": "2",
                    "unit": "stalks",
                    "purchase_likelihood": 0.7,  # LLM: higher
                },
            ],
        )

        result = compute_shopping_list(session, planning_session.id)

        # Carrots should be first (historical: always purchased)
        # Celery should be second (historical: always skipped, might even be pantry)
        grocery_names = [item.ingredient_name for item in result.grocery_items]
        if "celery" in grocery_names:
            # If celery is still in grocery, carrots should be first
            assert grocery_names[0] == "carrots"
        else:
            # Celery might have dropped to pantry
            assert len(result.grocery_items) == 1
            assert result.grocery_items[0].ingredient_name == "carrots"
