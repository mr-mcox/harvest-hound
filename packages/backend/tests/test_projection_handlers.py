"""
Test projection handlers with view stores.

Testing integration between projection handlers and view stores
using SQLAlchemy Core per ADR-005.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.events.domain_events import InventoryItemAdded, StoreCreated, IngredientCreated
from app.models import Ingredient, InventoryStore
from app.models.read_models import InventoryItemView, StoreView
from app.infrastructure.view_stores import InventoryItemViewStore, StoreViewStore
from app.projections.handlers import InventoryProjectionHandler, StoreProjectionHandler


class MockIngredientRepository:
    """Mock ingredient repository for testing."""
    
    def __init__(self):
        self._ingredients = {}
    
    def add_ingredient(self, ingredient: Ingredient):
        """Add ingredient to mock store."""
        self._ingredients[ingredient.ingredient_id] = ingredient
    
    def get_by_id(self, ingredient_id) -> Ingredient | None:
        """Get ingredient by ID."""
        return self._ingredients.get(ingredient_id)


class MockStoreRepository:
    """Mock store repository for testing."""
    
    def __init__(self):
        self._stores = {}
    
    def add_store(self, store: InventoryStore):
        """Add store to mock store."""
        self._stores[store.store_id] = store
    
    def get_by_id(self, store_id) -> InventoryStore | None:
        """Get store by ID."""
        return self._stores.get(store_id)


class TestInventoryProjectionHandler:
    """Test InventoryProjectionHandler with view stores."""

    @pytest.fixture
    def session(self):
        """Create test session with in-memory database."""
        engine = create_engine("sqlite:///:memory:")
        Session = sessionmaker(bind=engine)
        return Session()
    
    @pytest.fixture
    def ingredient_repo(self):
        """Create mock ingredient repository."""
        return MockIngredientRepository()
    
    @pytest.fixture
    def store_repo(self):
        """Create mock store repository."""
        return MockStoreRepository()
    
    @pytest.fixture
    def view_store(self, session):
        """Create SQLAlchemy view store."""
        return InventoryItemViewStore(session=session)
    
    @pytest.fixture
    def handler(self, ingredient_repo, store_repo, view_store):
        """Create projection handler with dependencies."""
        return InventoryProjectionHandler(
            ingredient_repo=ingredient_repo,
            store_repo=store_repo,
            view_store=view_store,
        )

    def test_handle_inventory_item_added_creates_view(self, handler, ingredient_repo, store_repo, view_store):
        """Handler should create InventoryItemView when processing InventoryItemAdded event."""
        # Arrange
        store_id = uuid4()
        ingredient_id = uuid4()
        added_at = datetime(2024, 1, 15, 14, 30)
        
        # Setup mock data
        ingredient = Ingredient(
            ingredient_id=ingredient_id,
            name="Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 1)
        )
        store = InventoryStore(
            store_id=store_id,
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            inventory_items=[]
        )
        
        ingredient_repo.add_ingredient(ingredient)
        store_repo.add_store(store)
        
        event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=ingredient_id,
            quantity=2.0,
            unit="lbs",
            notes="Fresh from farm",
            added_at=added_at,
        )
        
        # Act
        handler.handle_inventory_item_added(event)
        
        # Assert
        views = view_store.get_by_ingredient_id(ingredient_id)
        assert len(views) == 1
        
        view = views[0]
        assert view.store_id == store_id
        assert view.ingredient_id == ingredient_id
        assert view.ingredient_name == "Carrots"
        assert view.store_name == "CSA Box"
        assert view.quantity == 2.0
        assert view.unit == "lbs"
        assert view.notes == "Fresh from farm"

    def test_handle_ingredient_created_updates_existing_views(self, handler, ingredient_repo, store_repo, view_store):
        """Handler should update existing inventory views when ingredient is created/updated."""
        # Arrange
        ingredient_id = uuid4()
        store_id = uuid4()
        
        # Create existing view directly in view store
        existing_view = InventoryItemView(
            store_id=store_id,
            ingredient_id=ingredient_id,
            ingredient_name="Old Name",
            store_name="CSA Box",
            quantity=2.0,
            unit="lbs",
            notes=None,
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        view_store.save_inventory_item_view(existing_view)
        
        event = IngredientCreated(
            ingredient_id=ingredient_id,
            name="Updated Carrots",
            default_unit="lbs",
            created_at=datetime(2024, 1, 16),
        )
        
        # Act
        handler.handle_ingredient_created(event)
        
        # Assert
        views = view_store.get_by_ingredient_id(ingredient_id)
        assert len(views) == 1
        
        updated_view = views[0]
        assert updated_view.ingredient_name == "Updated Carrots"
        # Other fields should remain the same
        assert updated_view.store_id == store_id
        assert updated_view.quantity == 2.0


class TestStoreProjectionHandler:
    """Test StoreProjectionHandler with view stores."""

    @pytest.fixture
    def session(self):
        """Create test session with in-memory database."""
        engine = create_engine("sqlite:///:memory:")
        Session = sessionmaker(bind=engine)
        return Session()
    
    @pytest.fixture
    def view_store(self, session):
        """Create SQLAlchemy store view store."""
        return StoreViewStore(session=session)
    
    @pytest.fixture
    def handler(self, view_store):
        """Create projection handler with dependencies."""
        return StoreProjectionHandler(view_store=view_store)

    def test_handle_store_created_creates_view(self, handler, view_store):
        """Handler should create StoreView when processing StoreCreated event."""
        # Arrange
        store_id = uuid4()
        created_at = datetime(2024, 1, 15, 10, 0)
        
        event = StoreCreated(
            store_id=store_id,
            name="CSA Box",
            description="Weekly vegetable delivery",
            infinite_supply=False,
            created_at=created_at,
        )
        
        # Act
        handler.handle_store_created(event)
        
        # Assert
        view = view_store.get_by_store_id(store_id)
        assert view is not None
        assert view.store_id == store_id
        assert view.name == "CSA Box"
        assert view.description == "Weekly vegetable delivery"
        assert view.infinite_supply is False
        assert view.item_count == 0  # New store starts with 0 items

    def test_handle_inventory_item_added_updates_count(self, handler, view_store):
        """Handler should increment item_count when processing InventoryItemAdded event."""
        # Arrange
        store_id = uuid4()
        
        # Create existing store view
        existing_view = StoreView(
            store_id=store_id,
            name="CSA Box",
            description="Weekly delivery",
            infinite_supply=False,
            item_count=2,
            created_at=datetime(2024, 1, 15, 10, 0),
        )
        view_store.save_store_view(existing_view)
        
        event = InventoryItemAdded(
            store_id=store_id,
            ingredient_id=uuid4(),
            quantity=1.0,
            unit="bunch",
            notes=None,
            added_at=datetime(2024, 1, 15, 14, 30),
        )
        
        # Act
        handler.handle_inventory_item_added(event)
        
        # Assert
        updated_view = view_store.get_by_store_id(store_id)
        assert updated_view is not None
        assert updated_view.item_count == 3  # Should be incremented