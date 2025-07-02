import uuid
from datetime import datetime

from app.events import StoreCreated
from app.models import InventoryStore


def test_inventory_store_creation_generates_store_created_event():
    """Test that InventoryStore creation generates StoreCreated event"""
    # Arrange
    store_id = uuid.uuid4()
    name = "CSA Box"
    description = "Weekly vegetable delivery"
    infinite_supply = False

    # Act
    store = InventoryStore.create(
        store_id=store_id,
        name=name,
        description=description,
        infinite_supply=infinite_supply,
    )

    # Assert
    assert len(store.uncommitted_events) == 1
    event = store.uncommitted_events[0]
    assert isinstance(event, StoreCreated)
    assert event.store_id == store_id
    assert event.name == name
    assert event.description == description
    assert event.infinite_supply == infinite_supply
    assert isinstance(event.created_at, datetime)
