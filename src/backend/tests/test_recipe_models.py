"""
Tests for Recipe model with structured ingredients
"""

from sqlmodel import Session

from models import Recipe


class TestRecipeModel:
    """Tests for Recipe SQLModel"""

    def test_recipe_json_roundtrip(self, session: Session):
        """Ingredients survive database round-trip correctly"""
        ingredients = [
            {
                "name": "carrots",
                "quantity": "2",
                "unit": "pounds",
                "preparation": "julienned",
                "notes": "thin strips",
            }
        ]
        recipe = Recipe(
            name="Carrot Salad",
            description="Fresh and crunchy",
            ingredients=ingredients,
            instructions=["Cut carrots", "Dress and serve"],
            active_time_minutes=15,
            total_time_minutes=15,
            servings=4,
        )
        session.add(recipe)
        session.commit()

        # Clear session cache and reload
        session.expire_all()
        loaded = session.get(Recipe, recipe.id)

        assert loaded is not None
        assert loaded.ingredients == ingredients
        assert loaded.ingredients[0]["preparation"] == "julienned"
        assert loaded.ingredients[0]["notes"] == "thin strips"
