"""
Test SQLAlchemy-based view stores for read model persistence.

Testing the migration to SQLAlchemy Core as specified in ADR-005 for better
schema management, type safety, and database independence.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from app.models.read_models import InventoryItemView, StoreView
from app.infrastructure.sqlalchemy_view_stores import InventoryItemViewStore, StoreViewStore


class TestSQLAlchemyInventoryItemViewStore:
    """Test SQLAlchemy-based InventoryItemViewStore."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine):
        """Create test session."""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_save_and_retrieve_inventory_item_view(self, session):
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

    def test_get_all_for_store(self, session):
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

    def test_upsert_behavior(self, session):
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


class TestSQLAlchemyStoreViewStore:
    """Test SQLAlchemy-based StoreViewStore."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine):
        """Create test session."""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_save_and_retrieve_store_view(self, session):
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

    def test_get_all_stores(self, session):
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

    def test_get_by_store_id_not_found(self, session):
        """SQLAlchemy view store should return None for non-existent store."""
        # Arrange
        store = StoreViewStore(session=session)
        non_existent_id = uuid4()
        
        # Act
        result = store.get_by_store_id(non_existent_id)
        
        # Assert
        assert result is None