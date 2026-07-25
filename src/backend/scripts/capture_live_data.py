"""
Capture live data snapshot from harvest.db for priority pairing experiments.

This script exports household profile, pantry staples, grocery stores,
and inventory (with priorities) to JSON for repeatable testing of different
recipe generation approaches.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def capture_snapshot(db_path: str, output_path: str) -> dict:
    """
    Capture snapshot of database state.

    Args:
        db_path: Path to database file (e.g., 'harvest.db')
        output_path: Path to write JSON snapshot

    Returns:
        Dict with captured data
    """
    from sqlmodel import Session, select

    from models import (
        GroceryStore,
        HouseholdProfile,
        InventoryItem,
        Pantry,
        create_engine,
    )

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    with Session(engine) as session:
        household = session.exec(select(HouseholdProfile)).first()
        pantry = session.exec(select(Pantry)).first()
        stores = session.exec(select(GroceryStore)).all()
        inventory = session.exec(select(InventoryItem)).all()

        snapshot = {
            "household_profile": household.content if household else "",
            "pantry_staples": pantry.content if pantry else "",
            "grocery_stores": [
                {"name": store.name, "description": store.description}
                for store in stores
            ],
            "inventory": [
                {
                    "ingredient_name": item.ingredient_name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "priority": item.priority,
                    "store_id": item.store_id,
                }
                for item in inventory
            ],
            "metadata": {
                "captured_at": datetime.now().isoformat(),
                "inventory_count": len(inventory),
                "db_path": db_path,
            },
        }

        with open(output_path, "w") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot


def load_snapshot(snapshot_path: str) -> dict:
    """
    Load snapshot from JSON file.

    Args:
        snapshot_path: Path to snapshot JSON file

    Returns:
        Dict with snapshot data
    """
    with open(snapshot_path) as f:
        return json.load(f)


def main():
    """Capture live data from harvest.db"""
    script_dir = Path(__file__).parent
    backend_root = script_dir.parent
    db_path = backend_root / "harvest.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = script_dir / "snapshots" / f"harvest_snapshot_{timestamp}.json"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    print(f"Capturing snapshot from {db_path}...")
    snapshot = capture_snapshot(str(db_path), str(output_path))
    print(f"Snapshot saved to {output_path}")
    print(f"Captured {snapshot['metadata']['inventory_count']} inventory items")


if __name__ == "__main__":
    main()
