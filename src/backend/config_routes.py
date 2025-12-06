"""
Configuration API routes for Harvest Hound

Endpoints for managing singleton configs (HouseholdProfile, Pantry)
and CRUD for GroceryStore.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from models import HouseholdProfile, Pantry, get_session
from schemas import SingletonConfigResponse, SingletonConfigUpdate

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
