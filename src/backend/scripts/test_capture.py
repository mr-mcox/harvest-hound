"""
Tests for live data capture functionality.
"""

import json
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from scripts.capture_live_data import (  # noqa: E402
    capture_snapshot,
    load_snapshot,
)


class TestCaptureSnapshot:
    """Tests for capture_snapshot function"""

    def test_capture_includes_household_profile(self, tmp_path):
        """Captured snapshot should include household profile"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        snapshot = capture_snapshot(str(db_path), str(output_path))

        assert "household_profile" in snapshot
        assert isinstance(snapshot["household_profile"], str)

    def test_capture_includes_pantry_staples(self, tmp_path):
        """Captured snapshot should include pantry staples"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        snapshot = capture_snapshot(str(db_path), str(output_path))

        assert "pantry_staples" in snapshot
        assert isinstance(snapshot["pantry_staples"], str)

    def test_capture_includes_grocery_stores(self, tmp_path):
        """Captured snapshot should include grocery stores"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        snapshot = capture_snapshot(str(db_path), str(output_path))

        assert "grocery_stores" in snapshot
        assert isinstance(snapshot["grocery_stores"], list)

    def test_capture_includes_inventory_with_priorities(self, tmp_path):
        """Captured snapshot should include inventory items with all fields"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        snapshot = capture_snapshot(str(db_path), str(output_path))

        assert "inventory" in snapshot
        assert isinstance(snapshot["inventory"], list)

        if len(snapshot["inventory"]) > 0:
            item = snapshot["inventory"][0]
            assert "ingredient_name" in item
            assert "quantity" in item
            assert "unit" in item
            assert "priority" in item

    def test_capture_includes_metadata(self, tmp_path):
        """Captured snapshot should include metadata"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        snapshot = capture_snapshot(str(db_path), str(output_path))

        assert "metadata" in snapshot
        assert "captured_at" in snapshot["metadata"]
        assert "inventory_count" in snapshot["metadata"]

    def test_capture_writes_json_file(self, tmp_path):
        """Capture should write valid JSON file to disk"""
        backend_root = Path(__file__).parent.parent
        db_path = backend_root / "harvest.db"
        output_path = tmp_path / "test_snapshot.json"

        capture_snapshot(str(db_path), str(output_path))

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "inventory" in data


class TestLoadSnapshot:
    """Tests for load_snapshot function"""

    def test_load_reads_json_file(self, tmp_path):
        """Load should read JSON file and return dict"""
        snapshot_data = {
            "household_profile": "Test profile",
            "pantry_staples": "Test pantry",
            "grocery_stores": [],
            "inventory": [],
            "metadata": {"captured_at": "2025-01-01", "inventory_count": 0},
        }

        snapshot_path = tmp_path / "test_snapshot.json"
        with open(snapshot_path, "w") as f:
            json.dump(snapshot_data, f)

        loaded = load_snapshot(str(snapshot_path))

        assert loaded == snapshot_data

    def test_load_preserves_all_fields(self, tmp_path):
        """Load should preserve all snapshot fields"""
        snapshot_data = {
            "household_profile": "Family of 4",
            "pantry_staples": "Salt, pepper",
            "grocery_stores": [{"name": "Cub", "description": "Main store"}],
            "inventory": [
                {
                    "ingredient_name": "carrots",
                    "quantity": 2.0,
                    "unit": "pound",
                    "priority": "high",
                }
            ],
            "metadata": {"captured_at": "2025-01-01", "inventory_count": 1},
        }

        snapshot_path = tmp_path / "test_snapshot.json"
        with open(snapshot_path, "w") as f:
            json.dump(snapshot_data, f)

        loaded = load_snapshot(str(snapshot_path))

        assert loaded["household_profile"] == "Family of 4"
        assert loaded["inventory"][0]["priority"] == "high"
        assert loaded["metadata"]["inventory_count"] == 1
