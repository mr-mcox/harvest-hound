"""Test implementations of service protocols."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.interfaces.service import StoreServiceProtocol
from app.services.store_service import InventoryUploadResult


class MockStoreService:
    """Mock store service for testing."""

    def __init__(self) -> None:
        """Initialize with empty state."""
        self._stores: Dict[UUID, Dict[str, Any]] = {}
        self._inventory: Dict[UUID, List[Dict[str, Any]]] = {}

    def create_store(
        self,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> UUID:
        """Create a mock store."""
        store_id = uuid4()
        self._stores[store_id] = {
            "store_id": str(store_id),
            "name": name,
            "description": description,
            "infinite_supply": infinite_supply,
            "item_count": 0,
        }
        self._inventory[store_id] = []
        return store_id

    def upload_inventory(
        self,
        store_id: UUID,
        inventory_text: str,
    ) -> InventoryUploadResult:
        """Mock inventory upload (always succeeds with 2 items for standard test input)."""
        if store_id not in self._stores:
            return InventoryUploadResult.error_result(["Store not found"])
            
        if not inventory_text.strip():
            return InventoryUploadResult.success_result(0)
            
        # Mock standard test case
        if inventory_text == "2 lbs carrots, 1 bunch kale":
            items = [
                {
                    "store_id": str(store_id),
                    "ingredient_id": str(uuid4()),
                    "ingredient_name": "carrot",
                    "store_name": self._stores[store_id]["name"],
                    "quantity": 2.0,
                    "unit": "pound",
                    "notes": None,
                    "added_at": datetime(2024, 1, 1),
                },
                {
                    "store_id": str(store_id),
                    "ingredient_id": str(uuid4()),
                    "ingredient_name": "kale",
                    "store_name": self._stores[store_id]["name"],
                    "quantity": 1.0,
                    "unit": "bunch",
                    "notes": None,
                    "added_at": datetime(2024, 1, 1),
                },
            ]
            self._inventory[store_id].extend(items)
            self._stores[store_id]["item_count"] = len(self._inventory[store_id])
            return InventoryUploadResult.success_result(2)
            
        # Default: add 1 item for any other input
        item = {
            "store_id": str(store_id),
            "ingredient_id": str(uuid4()),
            "ingredient_name": "mock_item",
            "store_name": self._stores[store_id]["name"],
            "quantity": 1.0,
            "unit": "piece",
            "notes": None,
            "added_at": datetime(2024, 1, 1),
        }
        self._inventory[store_id].append(item)
        self._stores[store_id]["item_count"] = len(self._inventory[store_id])
        return InventoryUploadResult.success_result(1)

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Get all mock stores."""
        return list(self._stores.values())

    def get_store_inventory(self, store_id: UUID) -> List[Dict[str, Any]]:
        """Get mock inventory for a store."""
        if store_id not in self._stores:
            raise ValueError("Store not found")
        return self._inventory[store_id]


class FailingMockStoreService:
    """Mock store service that simulates failures."""

    def __init__(self, failure_mode: str = "not_found") -> None:
        """Initialize with failure mode.
        
        Args:
            failure_mode: Type of failure to simulate
        """
        self.failure_mode = failure_mode

    def create_store(
        self,
        name: str,
        description: str = "",
        infinite_supply: bool = False,
    ) -> UUID:
        """Simulate store creation failure."""
        if self.failure_mode == "validation":
            raise ValueError("Invalid store data")
        return uuid4()

    def upload_inventory(
        self,
        store_id: UUID,
        inventory_text: str,
    ) -> InventoryUploadResult:
        """Simulate inventory upload failures."""
        if self.failure_mode == "not_found":
            return InventoryUploadResult.error_result(["Store not found"])
        elif self.failure_mode == "parsing":
            return InventoryUploadResult.error_result(["Failed to parse inventory"])
        elif self.failure_mode == "timeout":
            return InventoryUploadResult.error_result(["Service timeout"])
        return InventoryUploadResult.success_result(0)

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Simulate store listing failure."""
        if self.failure_mode == "database":
            raise ConnectionError("Database connection failed")
        return []

    def get_store_inventory(self, store_id: UUID) -> List[Dict[str, Any]]:
        """Simulate inventory retrieval failure."""
        if self.failure_mode == "not_found":
            raise ValueError("Store not found")
        return []