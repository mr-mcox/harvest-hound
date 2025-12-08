"""
API routes for Harvest Hound
"""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from baml_client import b
from models import (
    GroceryStore,
    HouseholdProfile,
    IngredientClaim,
    InventoryItem,
    MealCriterion,
    Pantry,
    Pitch,
    PlanningSession,
    Recipe,
    RecipeState,
    _utc_now,
    db_health,
    get_session,
)
from schemas import (
    ClaimSummary,
    FleshedOutRecipe,
    FleshOutRequest,
    FleshOutResponse,
    RecipeIngredientResponse,
    RecipeLifecycleResponse,
)
from services import (
    calculate_available_inventory,
    create_recipe_with_claims,
    format_available_inventory,
)
from shopping_list import ShoppingListResponse, compute_shopping_list

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    """Health check endpoint - verifies stack is working"""
    return {
        "status": "healthy",
        "db_ok": db_health(),
    }


# --- Session CRUD ---


class SessionCreate(BaseModel):
    name: str


class SessionResponse(BaseModel):
    id: UUID
    name: str
    created_at: str

    @classmethod
    def from_model(cls, session: PlanningSession) -> "SessionResponse":
        return cls(
            id=session.id,
            name=session.name,
            created_at=session.created_at.isoformat(),
        )


@router.post("/sessions", status_code=201)
def create_session(
    data: SessionCreate, db: Session = Depends(get_session)
) -> SessionResponse:
    """Create a new planning session"""
    session = PlanningSession(name=data.name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse.from_model(session)


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_session)) -> list[SessionResponse]:
    """List all planning sessions, newest first"""
    sessions = db.exec(
        select(PlanningSession).order_by(PlanningSession.created_at.desc())
    ).all()
    return [SessionResponse.from_model(s) for s in sessions]


@router.get("/sessions/{session_id}")
def get_session_by_id(
    session_id: UUID, db: Session = Depends(get_session)
) -> SessionResponse:
    """Get a specific planning session by ID"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_model(session)


# --- Criteria CRUD ---


class CriterionCreate(BaseModel):
    description: str
    slots: int


class CriterionResponse(BaseModel):
    id: UUID
    description: str
    slots: int
    created_at: str

    @classmethod
    def from_model(cls, criterion: MealCriterion) -> "CriterionResponse":
        return cls(
            id=criterion.id,
            description=criterion.description,
            slots=criterion.slots,
            created_at=criterion.created_at.isoformat(),
        )


MAX_CRITERIA_PER_SESSION = 7


@router.post("/sessions/{session_id}/criteria", status_code=201)
def create_criterion(
    session_id: UUID, data: CriterionCreate, db: Session = Depends(get_session)
) -> CriterionResponse:
    """Create a new meal criterion for a session"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check max criteria limit
    existing_count = len(
        db.exec(
            select(MealCriterion).where(MealCriterion.session_id == session_id)
        ).all()
    )
    if existing_count >= MAX_CRITERIA_PER_SESSION:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_CRITERIA_PER_SESSION} criteria per session",
        )

    criterion = MealCriterion(
        session_id=session_id,
        description=data.description,
        slots=data.slots,
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return CriterionResponse.from_model(criterion)


@router.get("/sessions/{session_id}/criteria")
def list_criteria(
    session_id: UUID, db: Session = Depends(get_session)
) -> list[CriterionResponse]:
    """List all criteria for a session"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    criteria = db.exec(
        select(MealCriterion)
        .where(MealCriterion.session_id == session_id)
        .order_by(MealCriterion.created_at)
    ).all()
    return [CriterionResponse.from_model(c) for c in criteria]


@router.delete("/sessions/{session_id}/criteria/{criterion_id}", status_code=204)
def delete_criterion(
    session_id: UUID, criterion_id: UUID, db: Session = Depends(get_session)
) -> None:
    """Delete a criterion from a session"""
    criterion = db.get(MealCriterion, criterion_id)
    if not criterion or criterion.session_id != session_id:
        raise HTTPException(status_code=404, detail="Criterion not found")

    db.delete(criterion)
    db.commit()


# --- Pitches API ---


class PitchResponse(BaseModel):
    id: UUID
    criterion_id: UUID
    name: str
    blurb: str
    why_make_this: str
    inventory_ingredients: list[dict]
    active_time_minutes: int
    created_at: str

    @classmethod
    def from_model(cls, pitch: Pitch) -> "PitchResponse":
        return cls(
            id=pitch.id,
            criterion_id=pitch.criterion_id,
            name=pitch.name,
            blurb=pitch.blurb,
            why_make_this=pitch.why_make_this,
            inventory_ingredients=pitch.inventory_ingredients,
            active_time_minutes=pitch.active_time_minutes,
            created_at=pitch.created_at.isoformat(),
        )


@router.get("/sessions/{session_id}/pitches")
def list_pitches(
    session_id: UUID, db: Session = Depends(get_session)
) -> list[PitchResponse]:
    """List all pitches for a session, ordered by criterion and creation time"""
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all criteria for this session
    criteria = db.exec(
        select(MealCriterion).where(MealCriterion.session_id == session_id)
    ).all()
    criterion_ids = [c.id for c in criteria]

    if not criterion_ids:
        return []

    # Get all pitches for these criteria
    pitches = db.exec(
        select(Pitch)
        .where(Pitch.criterion_id.in_(criterion_ids))
        .order_by(Pitch.criterion_id, Pitch.created_at)
    ).all()

    return [PitchResponse.from_model(p) for p in pitches]


# --- Pitch Generation (SSE Streaming) ---


def _format_inventory_text(inventory_items: list[InventoryItem], db: Session) -> str:
    """Format inventory items grouped by store with priority"""
    inventory_by_store = {}
    for item in inventory_items:
        store = db.get(GroceryStore, item.store_id)
        store_name = store.name if store else "Unknown Store"
        if store_name not in inventory_by_store:
            inventory_by_store[store_name] = []
        inventory_by_store[store_name].append(item)

    inventory_text = ""
    for store_name, items in inventory_by_store.items():
        inventory_text += f"\n## {store_name}\n"
        for item in items:
            priority_label = f"({item.priority} priority)"
            inventory_text += (
                f"- {item.quantity} {item.unit} "
                f"{item.ingredient_name} {priority_label}\n"
            )
    return inventory_text


@router.get("/sessions/{session_id}/generate-pitches")
async def generate_pitches(session_id: UUID, db: Session = Depends(get_session)):
    """
    Generate recipe pitches for all criteria in a session via SSE streaming.
    Pitches are saved to database as they're generated.
    """

    async def stream_generation():
        try:
            # Verify session exists
            session = db.get(PlanningSession, session_id)
            if not session:
                error_data = json.dumps({"error": True, "message": "Session not found"})
                yield f"data: {error_data}\n\n"
                return

            # Load criteria for this session
            criteria = db.exec(
                select(MealCriterion)
                .where(MealCriterion.session_id == session_id)
                .order_by(MealCriterion.created_at)
            ).all()

            if not criteria:
                error_data = json.dumps(
                    {"error": True, "message": "No criteria found for session"}
                )
                yield f"data: {error_data}\n\n"
                return

            household_profile = db.exec(select(HouseholdProfile)).first()
            pantry = db.exec(select(Pantry)).first()
            grocery_stores = db.exec(select(GroceryStore)).all()

            # Available inventory = physical minus reserved claims (enables multi-wave)
            available_inventory = calculate_available_inventory(db)

            household_profile_text = (
                household_profile.content if household_profile else ""
            )
            pantry_text = pantry.content if pantry else ""
            grocery_stores_text = "\n".join(
                f"- {store.name}: {store.description}" for store in grocery_stores
            )
            inventory_text = format_available_inventory(available_inventory, db)

            total_criteria = len(criteria)
            for criterion_index, criterion in enumerate(criteria, start=1):
                num_pitches = 3 * criterion.slots

                progress_data = json.dumps(
                    {
                        "progress": True,
                        "criterion_index": criterion_index,
                        "total_criteria": total_criteria,
                        "criterion_description": criterion.description,
                        "generating_count": num_pitches,
                    }
                )
                yield f"data: {progress_data}\n\n"

                pitches = await b.GenerateRecipePitches(
                    inventory=inventory_text,
                    pantry_staples=pantry_text,
                    grocery_stores=grocery_stores_text,
                    household_profile=household_profile_text,
                    additional_context=criterion.description,
                    num_pitches=num_pitches,
                )

                for pitch_index, pitch in enumerate(pitches, start=1):
                    db_pitch = Pitch(
                        criterion_id=criterion.id,
                        name=pitch.name,
                        blurb=pitch.blurb,
                        why_make_this=pitch.why_make_this,
                        inventory_ingredients=[
                            {
                                "name": ing.name,
                                "quantity": ing.quantity,
                                "unit": ing.unit,
                            }
                            for ing in pitch.inventory_ingredients
                        ],
                        active_time_minutes=pitch.active_time_minutes,
                    )
                    db.add(db_pitch)
                    db.commit()
                    db.refresh(db_pitch)

                    # Stream pitch event
                    pitch_data = json.dumps(
                        {
                            "pitch": True,
                            "criterion_id": str(criterion.id),
                            "pitch_index": pitch_index,
                            "total_for_criterion": num_pitches,
                            "data": {
                                "id": str(db_pitch.id),
                                "name": db_pitch.name,
                                "blurb": db_pitch.blurb,
                                "why_make_this": db_pitch.why_make_this,
                                "inventory_ingredients": db_pitch.inventory_ingredients,
                                "active_time_minutes": db_pitch.active_time_minutes,
                            },
                        }
                    )
                    yield f"data: {pitch_data}\n\n"

            # Send completion event
            completion_data = json.dumps({"complete": True})
            yield f"data: {completion_data}\n\n"

        except Exception as e:
            error_data = json.dumps({"error": True, "message": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        stream_generation(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# --- Flesh-Out Pitches to Complete Recipes ---


@router.post("/sessions/{session_id}/flesh-out-pitches")
async def flesh_out_pitches(
    session_id: UUID,
    request: FleshOutRequest,
    db: Session = Depends(get_session),
) -> FleshOutResponse:
    """
    Flesh out selected pitches into complete recipes with ingredient claims.

    For each pitch:
    1. Call BAML FleshOutRecipe to generate complete recipe
    2. Save Recipe to database
    3. Create IngredientClaims for matching inventory items (atomic)

    Returns list of created recipes with their claims.
    """
    # Verify session exists
    session = db.get(PlanningSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Handle empty pitches list
    if not request.pitches:
        return FleshOutResponse(recipes=[], errors=[])

    # Load household context for BAML
    household_profile = db.exec(select(HouseholdProfile)).first()
    pantry = db.exec(select(Pantry)).first()
    grocery_stores = db.exec(select(GroceryStore)).all()
    inventory_items = db.exec(select(InventoryItem)).all()

    household_profile_text = household_profile.content if household_profile else ""
    pantry_text = pantry.content if pantry else ""
    grocery_stores_text = "\n".join(
        f"- {store.name}: {store.description}" for store in grocery_stores
    )
    inventory_text = _format_inventory_text(inventory_items, db)

    recipes_out = []
    errors = []

    for pitch in request.pitches:
        try:
            # Format pitch inventory ingredients for BAML
            pitch_ingredients_text = ", ".join(
                f"{ing['name']}: {ing['quantity']} {ing['unit']}"
                for ing in pitch.inventory_ingredients
            )

            # Call BAML to flesh out the pitch
            baml_recipe = await b.FleshOutRecipe(
                pitch_name=pitch.name,
                pitch_blurb=pitch.blurb,
                pitch_inventory_ingredients=pitch_ingredients_text,
                household_profile=household_profile_text,
                pantry_staples=pantry_text,
                grocery_stores=grocery_stores_text,
                inventory=inventory_text,
            )

            # Convert BAML output to recipe data dict
            recipe_data = {
                "name": baml_recipe.name,
                "description": baml_recipe.description,
                "ingredients": [
                    {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "preparation": ing.preparation,
                        "notes": ing.notes,
                    }
                    for ing in baml_recipe.ingredients
                ],
                "instructions": baml_recipe.instructions,
                "active_time_minutes": baml_recipe.active_time_minutes,
                "total_time_minutes": baml_recipe.total_time_minutes,
                "servings": baml_recipe.servings,
                "notes": baml_recipe.notes,
            }

            # Create recipe with atomic claim creation
            recipe, claims = create_recipe_with_claims(db, recipe_data)

            # Build response
            recipes_out.append(
                FleshedOutRecipe(
                    id=str(recipe.id),
                    name=recipe.name,
                    description=recipe.description,
                    ingredients=[
                        RecipeIngredientResponse(
                            name=ing["name"],
                            quantity=ing["quantity"],
                            unit=ing["unit"],
                            preparation=ing.get("preparation"),
                            notes=ing.get("notes"),
                        )
                        for ing in recipe.ingredients
                    ],
                    instructions=recipe.instructions,
                    active_time_minutes=recipe.active_time_minutes,
                    total_time_minutes=recipe.total_time_minutes,
                    servings=recipe.servings,
                    notes=recipe.notes,
                    claims=[
                        ClaimSummary(
                            ingredient_name=claim.ingredient_name,
                            quantity=claim.quantity,
                            unit=claim.unit,
                            inventory_item_id=claim.inventory_item_id,
                        )
                        for claim in claims
                    ],
                )
            )

        except Exception as e:
            errors.append(f"Failed to flesh out '{pitch.name}': {str(e)}")

    return FleshOutResponse(recipes=recipes_out, errors=errors)


# --- Recipe Lifecycle Endpoints ---


@router.post("/recipes/{recipe_id}/cook")
def cook_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_session),
) -> RecipeLifecycleResponse:
    """
    Mark a recipe as cooked: transition state, delete claims, decrement inventory.

    This is an atomic operation - all changes succeed or fail together.
    Idempotent: calling multiple times produces same result (no-op if already cooked).
    """
    # Get recipe
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Idempotency check: if already cooked, return early
    if recipe.state == RecipeState.COOKED:
        return RecipeLifecycleResponse(
            recipe_id=str(recipe_id),
            new_state=recipe.state.value,
            claims_deleted=0,
            inventory_items_decremented=0,
        )

    # Get all claims for this recipe
    claims = db.exec(
        select(IngredientClaim).where(IngredientClaim.recipe_id == recipe_id)
    ).all()

    # Track counts for response
    inventory_items_decremented = 0

    # Decrement inventory for each claim
    for claim in claims:
        inventory_item = db.get(InventoryItem, claim.inventory_item_id)
        if inventory_item:  # Handle staleness: item might be deleted
            inventory_item.quantity -= claim.quantity
            inventory_items_decremented += 1

    # Delete all claims
    claims_deleted = len(claims)
    for claim in claims:
        db.delete(claim)

    # Update recipe state
    recipe.state = RecipeState.COOKED
    recipe.cooked_at = _utc_now()

    # Commit transaction (atomic)
    db.commit()

    return RecipeLifecycleResponse(
        recipe_id=str(recipe_id),
        new_state=recipe.state.value,
        claims_deleted=claims_deleted,
        inventory_items_decremented=inventory_items_decremented,
    )


@router.post("/recipes/{recipe_id}/abandon")
def abandon_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_session),
) -> RecipeLifecycleResponse:
    """
    Mark a recipe as abandoned: transition state, delete claims (releases inventory).

    This is an atomic operation - all changes succeed or fail together.
    Idempotent: calling multiple times produces same result (no-op if already
    abandoned).
    """
    # Get recipe
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Idempotency check: if already abandoned, return early
    if recipe.state == RecipeState.ABANDONED:
        return RecipeLifecycleResponse(
            recipe_id=str(recipe_id),
            new_state=recipe.state.value,
            claims_deleted=0,
            inventory_items_decremented=0,
        )

    # Get all claims for this recipe
    claims = db.exec(
        select(IngredientClaim).where(IngredientClaim.recipe_id == recipe_id)
    ).all()

    # Delete all claims (releases inventory - no decrement)
    claims_deleted = len(claims)
    for claim in claims:
        db.delete(claim)

    # Update recipe state
    recipe.state = RecipeState.ABANDONED

    # Commit transaction (atomic)
    db.commit()

    return RecipeLifecycleResponse(
        recipe_id=str(recipe_id),
        new_state=recipe.state.value,
        claims_deleted=claims_deleted,
        inventory_items_decremented=0,  # Never decrement for abandon
    )


@router.get("/sessions/{session_id}/shopping-list")
def get_shopping_list(
    session_id: UUID,
    db: Session = Depends(get_session),
) -> ShoppingListResponse:
    """
    Get shopping list for a planning session.

    Returns force-ranked grocery items (purchase_likelihood >= 0.3) sorted by
    likelihood descending, plus pantry staples (likelihood < 0.3).

    Shopping list is computed on-demand from planned recipes, excluding
    ingredients with claims (already sourced from inventory).
    """
    # Verify session exists
    planning_session = db.get(PlanningSession, session_id)
    if not planning_session:
        raise HTTPException(status_code=404, detail="Planning session not found")

    # Compute and return shopping list
    return compute_shopping_list(db, session_id)
