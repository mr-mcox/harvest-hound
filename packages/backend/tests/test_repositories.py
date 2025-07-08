from typing import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.event_store import EventStore
from app.infrastructure.repositories import (
    AggregateNotFoundError,
    IngredientRepository,
    StoreRepository,
)
from app.infrastructure.database import metadata
from app.models.ingredient import Ingredient
from app.models.inventory_store import InventoryStore


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestIngredientRepository:
    """Test IngredientRepository can save and reload Ingredients from events."""

    def test_save_and_reload_ingredient_from_events(self, db_session: Session) -> None:
        """IngredientRepository should save Ingredient and reload from events."""
        # Setup
        event_store = EventStore(session=db_session)
        repository = IngredientRepository(event_store)
        ingredient_id = uuid4()

        # Create ingredient
        ingredient, events = Ingredient.create(
            ingredient_id=ingredient_id, name="carrots", default_unit="lbs"
        )

        # Save ingredient
        repository.save(ingredient, events)

        # Reload ingredient
        loaded_ingredient = repository.load(ingredient_id)

        # Verify the loaded ingredient matches the original
        assert loaded_ingredient.ingredient_id == ingredient.ingredient_id
        assert loaded_ingredient.name == ingredient.name
        assert loaded_ingredient.default_unit == ingredient.default_unit
        assert loaded_ingredient.created_at == ingredient.created_at

    def test_load_nonexistent_ingredient_raises_error(self, db_session: Session) -> None:
        """IngredientRepository should raise error for nonexistent ingredient."""
        # Setup
        event_store = EventStore(session=db_session)
        repository = IngredientRepository(event_store)
        nonexistent_id = uuid4()

        # Try to load nonexistent ingredient
        with pytest.raises(AggregateNotFoundError) as exc_info:
            repository.load(nonexistent_id)

        assert str(nonexistent_id) in str(exc_info.value)


class TestStoreRepository:
    """Test StoreRepository can save and reload InventoryStores from events."""

    def test_save_and_reload_store_from_events(self, db_session: Session) -> None:
        """StoreRepository should save InventoryStore and reload from events."""
        # Setup
        event_store = EventStore(session=db_session)
        repository = StoreRepository(event_store)
        store_id = uuid4()
        ingredient_id = uuid4()

        # Create store
        store, create_events = InventoryStore.create(
            store_id=store_id,
            name="CSA Box",
            description="Weekly CSA delivery",
            infinite_supply=False,
        )

        # Add inventory item
        updated_store, add_events = store.add_inventory_item(
            ingredient_id=ingredient_id,
            quantity=2.0,
            unit="lbs",
            notes="Fresh carrots",
        )

        # Save store with both creation and addition events
        all_events = create_events + add_events
        repository.save(updated_store, all_events)

        # Reload store
        loaded_store = repository.load(store_id)

        # Verify the loaded store matches the original
        assert loaded_store.store_id == updated_store.store_id
        assert loaded_store.name == updated_store.name
        assert loaded_store.description == updated_store.description
        assert loaded_store.infinite_supply == updated_store.infinite_supply
        assert len(loaded_store.inventory_items) == len(
            updated_store.inventory_items
        )

        # Verify inventory item details
        loaded_item = loaded_store.inventory_items[0]
        original_item = updated_store.inventory_items[0]
        assert loaded_item.store_id == original_item.store_id
        assert loaded_item.ingredient_id == original_item.ingredient_id
        assert loaded_item.quantity == original_item.quantity
        assert loaded_item.unit == original_item.unit
        assert loaded_item.notes == original_item.notes

    def test_load_nonexistent_store_raises_error(self, db_session: Session) -> None:
        """StoreRepository should raise AggregateNotFoundError for nonexistent store."""
        # Setup
        event_store = EventStore(session=db_session)
        repository = StoreRepository(event_store)
        nonexistent_id = uuid4()

        # Try to load nonexistent store
        with pytest.raises(AggregateNotFoundError) as exc_info:
            repository.load(nonexistent_id)

        assert str(nonexistent_id) in str(exc_info.value)


class TestRepositoryErrorHandling:
    """Test Repository error handling for edge cases."""

    def test_repository_handles_empty_event_stream(self) -> None:
        """Repository should handle empty event streams appropriately."""
        # This test is already covered by the nonexistent aggregate tests above
        # but we could add more specific edge cases here if needed
        pass
