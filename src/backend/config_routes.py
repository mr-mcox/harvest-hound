"""
Configuration API routes for Harvest Hound

Endpoints for managing singleton configs (HouseholdProfile, Pantry)
and CRUD for GroceryStore.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from models import GroceryStore, HouseholdProfile, Pantry, get_session
from schemas import (
    GroceryStoreCreate,
    GroceryStoreResponse,
    GroceryStoreUpdate,
    SingletonConfigResponse,
    SingletonConfigUpdate,
)

router = APIRouter(prefix="/api/config")


# Household Profile endpoints


@router.get("/household-profile", response_model=SingletonConfigResponse)
def get_household_profile(session: Session = Depends(get_session)):
    """Get current household profile configuration"""
    profile = session.exec(select(HouseholdProfile)).first()
    if profile is None:
        # Create default if not exists (shouldn't happen with seeding)
        profile = HouseholdProfile(content="")
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


@router.put("/household-profile", response_model=SingletonConfigResponse)
def put_household_profile(
    update: SingletonConfigUpdate,
    session: Session = Depends(get_session),
):
    """Update household profile configuration"""
    profile = session.exec(select(HouseholdProfile)).first()
    if profile is None:
        # Create if not exists (upsert pattern)
        profile = HouseholdProfile(content=update.content)
        session.add(profile)
    else:
        profile.content = update.content
        profile.updated_at = datetime.now(UTC)
    session.commit()
    session.refresh(profile)
    return profile


# Pantry endpoints


@router.get("/pantry", response_model=SingletonConfigResponse)
def get_pantry(session: Session = Depends(get_session)):
    """Get current pantry configuration"""
    pantry = session.exec(select(Pantry)).first()
    if pantry is None:
        # Create default if not exists (shouldn't happen with seeding)
        pantry = Pantry(content="")
        session.add(pantry)
        session.commit()
        session.refresh(pantry)
    return pantry


@router.put("/pantry", response_model=SingletonConfigResponse)
def put_pantry(
    update: SingletonConfigUpdate,
    session: Session = Depends(get_session),
):
    """Update pantry configuration"""
    pantry = session.exec(select(Pantry)).first()
    if pantry is None:
        # Create if not exists (upsert pattern)
        pantry = Pantry(content=update.content)
        session.add(pantry)
    else:
        pantry.content = update.content
        pantry.updated_at = datetime.now(UTC)
    session.commit()
    session.refresh(pantry)
    return pantry


# Grocery Store endpoints


@router.get("/grocery-stores", response_model=list[GroceryStoreResponse])
def list_grocery_stores(session: Session = Depends(get_session)):
    """List all grocery stores, ordered by created_at"""
    stores = session.exec(select(GroceryStore).order_by(GroceryStore.created_at)).all()
    return stores


@router.post("/grocery-stores", response_model=GroceryStoreResponse, status_code=201)
def create_grocery_store(
    store: GroceryStoreCreate,
    session: Session = Depends(get_session),
):
    """Create a new grocery store"""
    db_store = GroceryStore(name=store.name, description=store.description)
    session.add(db_store)
    session.commit()
    session.refresh(db_store)
    return db_store


@router.get("/grocery-stores/{store_id}", response_model=GroceryStoreResponse)
def get_grocery_store(store_id: int, session: Session = Depends(get_session)):
    """Get a specific grocery store by ID"""
    store = session.get(GroceryStore, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Grocery store not found")
    return store


@router.put("/grocery-stores/{store_id}", response_model=GroceryStoreResponse)
def update_grocery_store(
    store_id: int,
    update: GroceryStoreUpdate,
    session: Session = Depends(get_session),
):
    """Update a grocery store"""
    store = session.get(GroceryStore, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Grocery store not found")

    if update.name is not None:
        store.name = update.name
    if update.description is not None:
        store.description = update.description

    session.commit()
    session.refresh(store)
    return store


@router.delete("/grocery-stores/{store_id}", status_code=204)
def delete_grocery_store(store_id: int, session: Session = Depends(get_session)):
    """Delete a grocery store (cannot delete last store)"""
    store = session.get(GroceryStore, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Grocery store not found")

    count = len(session.exec(select(GroceryStore)).all())
    if count <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last grocery store. At least one must exist.",
        )

    session.delete(store)
    session.commit()
    return None
