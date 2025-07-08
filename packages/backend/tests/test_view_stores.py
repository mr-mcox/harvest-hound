"""
Test view stores for read model persistence.

Testing view stores using SQLAlchemy Core as specified in ADR-005 for better
schema management, type safety, and database independence.
"""
from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, MetaData, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.read_models import InventoryItemView, StoreView
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore


class TestInventoryItemViewStore:
    """Test InventoryItemViewStore."""

    @pytest.fixture
    def engine(self) -> Engine:
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine: Engine) -> Session:
        """Create test session."""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_save_and_retrieve_inventory_item_view(self, session: Session) -> None:
        """SQLAlchemy view store should save and retrieve InventoryItemView."""
        # Arrange
        store = InventoryItemViewStore(session=session)
        
        view = InventoryItemView(
            store_id=uuid4(),
            ingredient_id=uuid4(),
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        # Act
        store.save_inventory_item_view(view)
        retrieved_views = store.get_by_ingredient_id(view.ingredient_id)
        
        # Assert
        assert len(retrieved_views) == 1
        retrieved = retrieved_views[0]
        assert retrieved.store_id == view.store_id
        assert retrieved.ingredient_id == view.ingredient_id
        assert retrieved.ingredient_name == view.ingredient_name
        assert retrieved.store_name == view.store_name
        assert retrieved.quantity == view.quantity
        assert retrieved.unit == view.unit
        assert retrieved.notes == view.notes

    def test_get_all_for_store(self, session: Session) -> None:
        """SQLAlchemy view store should retrieve all views for a store."""
        # Arrange
        store = InventoryItemViewStore(session=session)
        store_id = uuid4()
        
        view1 = InventoryItemView(
            store_id=store_id,
            ingredient_id=uuid4(),
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes=None,
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        view2 = InventoryItemView(
            store_id=store_id,
            ingredient_id=uuid4(),
            ingredient_name="Kale",
            store_name="CSA Box",
            quantity=1.0,
            unit="bunch",
            notes="Organic",
            added_at=datetime(2024, 1, 15, 15, 0),
        )
        
        # Act
        store.save_inventory_item_view(view1)
        store.save_inventory_item_view(view2)
        views = store.get_all_for_store(store_id)
        
        # Assert
        assert len(views) == 2
        ingredient_names = {v.ingredient_name for v in views}
        assert ingredient_names == {"Carrots", "Kale"}

    def test_upsert_behavior(self, session: Session) -> None:
        """SQLAlchemy view store should update existing records on conflict."""
        # Arrange
        store = InventoryItemViewStore(session=session)
        store_id = uuid4()
        ingredient_id = uuid4()
        
        view1 = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Original",
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        view2 = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Organic Carrots",  # Updated name
            store_name="CSA Box",
            quantity=3.0,  # Updated quantity
            unit="lbs",
            notes="Updated",
            added_at=datetime(2024, 1, 15, 15, 0),
        )
        
        # Act
        store.save_inventory_item_view(view1)
        store.save_inventory_item_view(view2)  # Should update, not duplicate
        views = store.get_all_for_store(store_id)
        
        # Assert
        assert len(views) == 1  # Should be only one record
        updated = views[0]
        assert updated.ingredient_name == "Organic Carrots"
        assert updated.quantity == 3.0
        assert updated.notes == "Updated"

    def test_complete_read_model_roundtrip_with_complex_data(self, session: Session) -> None:
        """Test complete roundtrip persistence with complex denormalized data scenarios."""
        # Arrange
        store = InventoryItemViewStore(session=session)
        store_id1 = uuid4()
        store_id2 = uuid4()
        ingredient_id = uuid4()
        
        # Create views for same ingredient across different stores (denormalized data)
        view1 = InventoryItemView(
            store_id=store_id1,
            ingredient_id=ingredient_id,
            ingredient_name="Organic Carrots",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes="Fresh from local farm",
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        view2 = InventoryItemView(
            store_id=store_id2,
            ingredient_id=ingredient_id,
            ingredient_name="Organic Carrots",
            store_name="Pantry Store",
            quantity=1.5,
            unit="lbs", 
            notes="Backup supply",
            added_at=datetime(2024, 1, 16, 10, 0),
        )
        
        # Act - Save both views
        store.save_inventory_item_view(view1)
        store.save_inventory_item_view(view2)
        
        # Assert - Verify complete roundtrip through different query methods
        # Query by ingredient_id should return both stores
        by_ingredient = store.get_by_ingredient_id(ingredient_id)
        assert len(by_ingredient) == 2
        
        # Query by store should return one item each
        store1_items = store.get_all_for_store(store_id1)
        store2_items = store.get_all_for_store(store_id2)
        assert len(store1_items) == 1
        assert len(store2_items) == 1
        
        # Verify denormalized data integrity
        store1_item = store1_items[0]
        store2_item = store2_items[0]
        
        assert store1_item.store_name == "CSA Box"
        assert store2_item.store_name == "Pantry Store"
        assert store1_item.ingredient_name == store2_item.ingredient_name == "Organic Carrots"
        assert store1_item.ingredient_id == store2_item.ingredient_id == ingredient_id
        
        # Verify unique constraints work (same store + ingredient)
        # Update should not create duplicate
        updated_view = InventoryItemView(
            store_id=store_id1,
            ingredient_id=ingredient_id,
            ingredient_name="Premium Organic Carrots",  # Updated name
            store_name="CSA Box", 
            quantity=2.5,  # Updated quantity
            unit="lbs",
            notes="Extra fresh batch",
            added_at=datetime(2024, 1, 17, 9, 0),
        )
        
        store.save_inventory_item_view(updated_view)
        
        # Should still be 2 total items, but store1 should be updated
        final_by_ingredient = store.get_by_ingredient_id(ingredient_id)
        assert len(final_by_ingredient) == 2
        
        final_store1_items = store.get_all_for_store(store_id1)
        assert len(final_store1_items) == 1
        assert final_store1_items[0].ingredient_name == "Premium Organic Carrots"
        assert final_store1_items[0].quantity == 2.5


class TestStoreViewStore:
    """Test StoreViewStore."""

    @pytest.fixture
    def engine(self) -> Engine:
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine: Engine) -> Session:
        """Create test session."""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_save_and_retrieve_store_view(self, session: Session) -> None:
        """SQLAlchemy view store should save and retrieve StoreView."""
        # Arrange
        store = StoreViewStore(session=session)
        
        view = StoreView(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=5,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act
        store.save_store_view(view)
        retrieved = store.get_by_store_id(view.store_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.store_id == view.store_id
        assert retrieved.name == view.name
        assert retrieved.description == view.description
        assert retrieved.infinite_supply == view.infinite_supply
        assert retrieved.item_count == view.item_count

    def test_get_all_stores(self, session: Session) -> None:
        """SQLAlchemy view store should retrieve all store views."""
        # Arrange
        store = StoreViewStore(session=session)
        
        view1 = StoreView(
            store_id=uuid4(),
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            item_count=5,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        view2 = StoreView(
            store_id=uuid4(),
            name="Pantry",
            description="",
            infinite_supply=True,
            item_count=10,
            created_at=datetime(2024, 1, 10, 9, 0),
        )
        
        # Act
        store.save_store_view(view1)
        store.save_store_view(view2)
        views = store.get_all_stores()
        
        # Assert
        assert len(views) == 2
        names = {v.name for v in views}
        assert names == {"CSA Box", "Pantry"}

    def test_get_by_store_id_not_found(self, session: Session) -> None:
        """SQLAlchemy view store should return None for non-existent store."""
        # Arrange
        store = StoreViewStore(session=session)
        non_existent_id = uuid4()
        
        # Act
        result = store.get_by_store_id(non_existent_id)
        
        # Assert
        assert result is None

    def test_complete_store_view_roundtrip_with_item_count_updates(self, session: Session) -> None:
        """Test complete store view roundtrip with item count management."""
        # Arrange
        store = StoreViewStore(session=session)
        store_id = uuid4()
        
        # Initial store creation
        initial_view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=0,  # Starts empty
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Act - Save initial view
        store.save_store_view(initial_view)
        
        # Assert - Verify initial roundtrip
        retrieved = store.get_by_store_id(store_id)
        assert retrieved is not None
        assert retrieved.store_id == store_id
        assert retrieved.name == "CSA Box"
        assert retrieved.item_count == 0
        assert retrieved.infinite_supply is False
        
        # Simulate item count updates through multiple saves (upsert behavior)
        updated_view1 = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=2,  # Items added
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        updated_view2 = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            item_count=5,  # More items added
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        # Apply updates
        store.save_store_view(updated_view1)
        after_first_update = store.get_by_store_id(store_id)
        assert after_first_update is not None
        assert after_first_update.item_count == 2
        
        store.save_store_view(updated_view2)
        after_second_update = store.get_by_store_id(store_id)
        assert after_second_update is not None
        assert after_second_update.item_count == 5
        
        # Verify only one record exists (upsert, not insert)
        all_stores = store.get_all_stores()
        matching_stores = [s for s in all_stores if s.store_id == store_id]
        assert len(matching_stores) == 1
        assert matching_stores[0].item_count == 5
        
        # Test infinite supply toggle
        infinite_supply_view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=True,  # Changed to infinite
            item_count=5,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        
        store.save_store_view(infinite_supply_view)
        final_view = store.get_by_store_id(store_id)
        assert final_view is not None
        assert final_view.infinite_supply is True
        assert final_view.item_count == 5

    def test_store_view_query_operations_comprehensive(self, session: Session) -> None:
        """Test comprehensive querying scenarios for store views."""
        # Arrange
        store = StoreViewStore(session=session)
        
        # Create multiple stores with different characteristics
        stores_data = [
            ("CSA Box", "Fresh weekly delivery", False, 5),
            ("Pantry", "Long-term storage", True, 15),
            ("Freezer", "Frozen goods storage", True, 8),
            ("Emergency Supply", "Emergency backup", False, 0),
        ]
        
        store_views = []
        for i, (name, desc, infinite, count) in enumerate(stores_data):
            view = StoreView(
                store_id=uuid4(),
                name=name,
                description=desc,
                infinite_supply=infinite,
                item_count=count,
                created_at=datetime(2024, 1, 15 + i, 10, 0),  # Different dates
            )
            store_views.append(view)
            store.save_store_view(view)
        
        # Act & Assert - Test various query scenarios
        # Get all stores
        all_stores = store.get_all_stores()
        assert len(all_stores) == 4
        
        # Verify data integrity
        names = {s.name for s in all_stores}
        assert names == {"CSA Box", "Pantry", "Freezer", "Emergency Supply"}
        
        # Test individual retrieval
        for view in store_views:
            retrieved = store.get_by_store_id(view.store_id)
            assert retrieved is not None
            assert retrieved.name == view.name
            assert retrieved.item_count == view.item_count
            assert retrieved.infinite_supply == view.infinite_supply
        
        # Test non-existent store
        fake_id = uuid4()
        non_existent = store.get_by_store_id(fake_id)
        assert non_existent is None
        
        # Verify query consistency - multiple calls should return same data
        first_call = store.get_all_stores()
        second_call = store.get_all_stores()
        assert len(first_call) == len(second_call)
        
        # Sort by store_id for comparison
        first_sorted = sorted(first_call, key=lambda s: str(s.store_id))
        second_sorted = sorted(second_call, key=lambda s: str(s.store_id))
        
        for i in range(len(first_sorted)):
            assert first_sorted[i].store_id == second_sorted[i].store_id
            assert first_sorted[i].name == second_sorted[i].name
            assert first_sorted[i].item_count == second_sorted[i].item_count