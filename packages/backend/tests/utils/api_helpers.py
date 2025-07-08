"""Typed API testing utilities."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi.testclient import TestClient


def create_store(
    client: TestClient,
    name: str,
    description: str = "",
    infinite_supply: bool = False
) -> Dict[str, Any]:
    """Create a store via API and return response data.
    
    Args:
        client: Test client
        name: Store name
        description: Store description
        infinite_supply: Whether store has infinite supply
        
    Returns:
        Store creation response data
        
    Raises:
        AssertionError: If store creation fails
    """
    response = client.post("/stores", json={
        "name": name,
        "description": description,
        "infinite_supply": infinite_supply
    })
    assert response.status_code == 201, f"Failed to create store: {response.text}"
    data: Dict[str, Any] = response.json()
    return data


def upload_inventory(
    client: TestClient,
    store_id: UUID,
    inventory_text: str
) -> Dict[str, Any]:
    """Upload inventory via API and return response data.
    
    Args:
        client: Test client
        store_id: Store ID to upload to
        inventory_text: Inventory text to upload
        
    Returns:
        Upload response data
        
    Raises:
        AssertionError: If upload fails with unexpected status
    """
    response = client.post(
        f"/stores/{store_id}/inventory",
        json={"inventory_text": inventory_text}
    )
    assert response.status_code in [200, 201, 400], f"Unexpected status: {response.status_code}"
    data: Dict[str, Any] = response.json()
    return data


def get_store_inventory(
    client: TestClient,
    store_id: UUID
) -> List[Dict[str, Any]]:
    """Get store inventory via API.
    
    Args:
        client: Test client
        store_id: Store ID to get inventory for
        
    Returns:
        List of inventory items
        
    Raises:
        AssertionError: If retrieval fails
    """
    response = client.get(f"/stores/{store_id}/inventory")
    assert response.status_code == 200, f"Failed to get inventory: {response.text}"
    data: List[Dict[str, Any]] = response.json()
    return data


def get_all_stores(client: TestClient) -> List[Dict[str, Any]]:
    """Get all stores via API.
    
    Args:
        client: Test client
        
    Returns:
        List of stores
        
    Raises:
        AssertionError: If retrieval fails
    """
    response = client.get("/stores")
    assert response.status_code == 200, f"Failed to get stores: {response.text}"
    data: List[Dict[str, Any]] = response.json()
    return data


def find_inventory_item_by_name(
    inventory: List[Dict[str, Any]],
    ingredient_name: str
) -> Dict[str, Any]:
    """Find inventory item by ingredient name.
    
    Args:
        inventory: List of inventory items
        ingredient_name: Name to search for
        
    Returns:
        Matching inventory item
        
    Raises:
        AssertionError: If item not found
    """
    item = next(
        (item for item in inventory if ingredient_name in item["ingredient_name"].lower()),
        None
    )
    assert item is not None, f"Ingredient '{ingredient_name}' not found in inventory"
    return item


def find_store_by_name(
    stores: List[Dict[str, Any]],
    store_name: str
) -> Dict[str, Any]:
    """Find store by name.
    
    Args:
        stores: List of stores
        store_name: Name to search for
        
    Returns:
        Matching store
        
    Raises:
        AssertionError: If store not found
    """
    store = next(
        (store for store in stores if store["name"] == store_name),
        None
    )
    assert store is not None, f"Store '{store_name}' not found"
    return store