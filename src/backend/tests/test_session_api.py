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

    def test_delete_criterion(self, client):
        """DELETE removes a criterion"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()
        criterion = client.post(
            f"/api/sessions/{session['id']}/criteria",
            json={"description": "To delete", "slots": 1},
        ).json()

        response = client.delete(
            f"/api/sessions/{session['id']}/criteria/{criterion['id']}"
        )

        assert response.status_code == 204
        # Verify it's gone
        criteria = client.get(f"/api/sessions/{session['id']}/criteria").json()
        assert len(criteria) == 0

    def test_delete_criterion_not_found(self, client):
        """DELETE returns 404 for non-existent criterion"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(f"/api/sessions/{session['id']}/criteria/{fake_id}")

        assert response.status_code == 404

    def test_create_criterion_max_7_enforced(self, client):
        """POST returns 400 when session already has 7 criteria"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()

        # Create 7 criteria (max allowed)
        for i in range(7):
            response = client.post(
                f"/api/sessions/{session['id']}/criteria",
                json={"description": f"Criterion {i + 1}", "slots": 1},
            )
            assert response.status_code == 201

        # 8th should fail
        response = client.post(
            f"/api/sessions/{session['id']}/criteria",
            json={"description": "One too many", "slots": 1},
        )

        assert response.status_code == 400
        assert "maximum" in response.json()["detail"].lower()

    def test_list_criteria_empty(self, client):
        """GET returns empty list when no criteria exist"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()

        response = client.get(f"/api/sessions/{session['id']}/criteria")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_criteria_returns_created(self, client):
        """GET returns criteria after creation"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()
        client.post(
            f"/api/sessions/{session['id']}/criteria",
            json={"description": "Quick meals", "slots": 2},
        )
        client.post(
            f"/api/sessions/{session['id']}/criteria",
            json={"description": "Weekend cooking", "slots": 1},
        )

        response = client.get(f"/api/sessions/{session['id']}/criteria")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        descriptions = [c["description"] for c in data]
        assert "Quick meals" in descriptions
        assert "Weekend cooking" in descriptions


class TestCriteriaAPI:
    """Tests for /api/sessions/{id}/criteria endpoints"""

    def test_create_criterion(self, client):
        """POST creates a criterion for a session"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()

        response = client.post(
            f"/api/sessions/{session['id']}/criteria",
            json={"description": "Quick weeknight meals", "slots": 3},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Quick weeknight meals"
        assert data["slots"] == 3
        assert "id" in data

    def test_create_criterion_session_not_found(self, client):
        """POST returns 404 for non-existent session"""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.post(
            f"/api/sessions/{fake_id}/criteria",
            json={"description": "Test", "slots": 1},
        )

        assert response.status_code == 404


class TestPitchesAPI:
    """Tests for /api/sessions/{id}/pitches endpoints"""

    def test_list_pitches_empty(self, client):
        """GET returns empty list when no pitches exist"""
        session = client.post("/api/sessions", json={"name": "Test"}).json()

        response = client.get(f"/api/sessions/{session['id']}/pitches")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_pitches_returns_created(self, client, session):
        """GET returns pitches grouped by criterion"""
        from models import (
            GroceryStore,
            InventoryItem,
            MealCriterion,
            Pitch,
            PlanningSession,
        )

        # Create session with criteria and pitches directly in DB
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion1 = MealCriterion(
            session_id=planning_session.id,
            description="Quick meals",
            slots=2,
        )
        criterion2 = MealCriterion(
            session_id=planning_session.id,
            description="Weekend cooking",
            slots=1,
        )
        session.add(criterion1)
        session.add(criterion2)
        session.commit()
        session.refresh(criterion1)
        session.refresh(criterion2)

        # Create store with inventory for the pitches
        store = GroceryStore(name="CSA Box", description="Weekly delivery")
        session.add(store)
        session.commit()
        session.refresh(store)

        # Add inventory items for the pitches
        bok_choy = InventoryItem(
            store_id=store.id,
            ingredient_name="bok choy",
            quantity=2.0,
            unit="bunch",
        )
        carrots = InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=3.0,
            unit="lb",
        )
        session.add_all([bok_choy, carrots])
        session.commit()

        # Add pitches for criterion1
        pitch1 = Pitch(
            criterion_id=criterion1.id,
            name="Quick Stir Fry",
            blurb="A fast weeknight meal",
            why_make_this="Uses CSA veggies",
            inventory_ingredients=[
                {"name": "bok choy", "quantity": 1, "unit": "bunch"}
            ],
            active_time_minutes=15,
        )
        pitch2 = Pitch(
            criterion_id=criterion1.id,
            name="Simple Pasta",
            blurb="Comfort food",
            why_make_this="Kid-friendly",
            inventory_ingredients=[],
            active_time_minutes=20,
        )
        # Add pitch for criterion2
        pitch3 = Pitch(
            criterion_id=criterion2.id,
            name="Slow Roast",
            blurb="Weekend project",
            why_make_this="Perfect for lazy Sunday",
            inventory_ingredients=[{"name": "carrots", "quantity": 2, "unit": "lb"}],
            active_time_minutes=30,
        )
        session.add_all([pitch1, pitch2, pitch3])
        session.commit()

        # Fetch via API
        response = client.get(f"/api/sessions/{planning_session.id}/pitches")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify pitch fields
        names = [p["name"] for p in data]
        assert "Quick Stir Fry" in names
        assert "Simple Pasta" in names
        assert "Slow Roast" in names

        # Verify pitch has all required fields
        pitch = next(p for p in data if p["name"] == "Quick Stir Fry")
        assert pitch["blurb"] == "A fast weeknight meal"
        assert pitch["why_make_this"] == "Uses CSA veggies"
        assert pitch["inventory_ingredients"] == [
            {"name": "bok choy", "quantity": 1, "unit": "bunch"}
        ]
        assert pitch["active_time_minutes"] == 15
        assert "criterion_id" in pitch

    def test_list_pitches_session_not_found(self, client):
        """GET returns 404 for non-existent session"""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(f"/api/sessions/{fake_id}/pitches")

        assert response.status_code == 404

    def test_list_pitches_filters_invalid_pitches_based_on_inventory(
        self, client, session
    ):
        """GET returns only valid pitches that can be made with available inventory"""
        from models import (
            GroceryStore,
            InventoryItem,
            MealCriterion,
            Pitch,
            PlanningSession,
        )

        # Create session with criterion
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion = MealCriterion(
            session_id=planning_session.id,
            description="Quick meals",
            slots=2,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        # Create store with inventory
        store = GroceryStore(name="CSA Box", description="Weekly delivery")
        session.add(store)
        session.commit()
        session.refresh(store)

        # Create inventory items
        carrots = InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=3.0,
            unit="pounds",
        )
        onions = InventoryItem(
            store_id=store.id,
            ingredient_name="onions",
            quantity=2.0,
            unit="whole",
        )
        session.add_all([carrots, onions])
        session.commit()
        session.refresh(carrots)
        session.refresh(onions)

        # Create pitches
        valid_pitch = Pitch(
            criterion_id=criterion.id,
            name="Carrot Soup",
            blurb="Uses carrots",
            why_make_this="Good soup",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 2.0, "unit": "pounds"}
            ],
            active_time_minutes=30,
        )

        invalid_pitch_missing = Pitch(
            criterion_id=criterion.id,
            name="Potato Soup",
            blurb="Needs potatoes",
            why_make_this="Comfort food",
            inventory_ingredients=[
                {
                    "name": "potatoes",
                    "quantity": 3.0,
                    "unit": "pounds",
                }  # Not in inventory
            ],
            active_time_minutes=40,
        )

        invalid_pitch_unit_mismatch = Pitch(
            criterion_id=criterion.id,
            name="Onion Salad",
            blurb="Wrong units",
            why_make_this="Fresh salad",
            inventory_ingredients=[
                {
                    "name": "onions",
                    "quantity": 1.0,
                    "unit": "cups",
                }  # Have 'whole', need 'cups'
            ],
            active_time_minutes=10,
        )

        invalid_pitch_insufficient = Pitch(
            criterion_id=criterion.id,
            name="Lots of Carrots",
            blurb="Too many carrots",
            why_make_this="Carrot overload",
            inventory_ingredients=[
                {
                    "name": "carrots",
                    "quantity": 5.0,
                    "unit": "pounds",
                }  # Only have 3 pounds
            ],
            active_time_minutes=60,
        )

        session.add_all(
            [
                valid_pitch,
                invalid_pitch_missing,
                invalid_pitch_unit_mismatch,
                invalid_pitch_insufficient,
            ]
        )
        session.commit()

        # Fetch pitches via API
        response = client.get(f"/api/sessions/{planning_session.id}/pitches")

        assert response.status_code == 200
        data = response.json()

        # Only the valid pitch should be returned
        assert len(data) == 1
        assert data[0]["name"] == "Carrot Soup"

    def test_list_pitches_accounts_for_reserved_claims(self, client, session):
        """GET filters pitches based on available inventory minus reserved claims"""
        from models import (
            ClaimState,
            GroceryStore,
            IngredientClaim,
            InventoryItem,
            MealCriterion,
            Pitch,
            PlanningSession,
            Recipe,
            RecipeState,
        )

        # Create session with criterion
        planning_session = PlanningSession(name="Test Session")
        session.add(planning_session)
        session.commit()
        session.refresh(planning_session)

        criterion = MealCriterion(
            session_id=planning_session.id,
            description="Quick meals",
            slots=3,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        # Create store with inventory
        store = GroceryStore(name="CSA Box", description="Weekly delivery")
        session.add(store)
        session.commit()
        session.refresh(store)

        # Create inventory: 5 pounds of carrots
        carrots = InventoryItem(
            store_id=store.id,
            ingredient_name="carrots",
            quantity=5.0,
            unit="pounds",
        )
        session.add(carrots)
        session.commit()
        session.refresh(carrots)

        # Create a recipe that claims 3 pounds of carrots
        existing_recipe = Recipe(
            session_id=planning_session.id,
            criterion_id=criterion.id,
            name="Existing Carrot Recipe",
            description="Uses some carrots",
            ingredients=[{"name": "carrots", "quantity": "3", "unit": "pounds"}],
            instructions=["Cook carrots"],
            active_time_minutes=20,
            total_time_minutes=40,
            servings=4,
            state=RecipeState.PLANNED,
        )
        session.add(existing_recipe)
        session.commit()
        session.refresh(existing_recipe)

        # Create a RESERVED claim for 3 pounds of carrots
        claim = IngredientClaim(
            recipe_id=existing_recipe.id,
            inventory_item_id=carrots.id,
            ingredient_name="carrots",
            quantity=3.0,
            unit="pounds",
            state=ClaimState.RESERVED,
        )
        session.add(claim)
        session.commit()

        # Create pitches
        # Available: 5 - 3 = 2 pounds of carrots
        valid_pitch = Pitch(
            criterion_id=criterion.id,
            name="Small Carrot Salad",
            blurb="Uses 1 pound",
            why_make_this="Light meal",
            inventory_ingredients=[
                {"name": "carrots", "quantity": 1.0, "unit": "pounds"}  # Valid (1 <= 2)
            ],
            active_time_minutes=15,
        )

        invalid_pitch = Pitch(
            criterion_id=criterion.id,
            name="Big Carrot Soup",
            blurb="Uses 4 pounds",
            why_make_this="Hearty soup",
            inventory_ingredients=[
                {
                    "name": "carrots",
                    "quantity": 4.0,
                    "unit": "pounds",
                }  # Invalid (4 > 2 available)
            ],
            active_time_minutes=45,
        )

        session.add_all([valid_pitch, invalid_pitch])
        session.commit()

        # Fetch pitches via API
        response = client.get(f"/api/sessions/{planning_session.id}/pitches")

        assert response.status_code == 200
        data = response.json()

        # Only the valid pitch should be returned (after accounting for reserved claims)
        assert len(data) == 1
        assert data[0]["name"] == "Small Carrot Salad"
