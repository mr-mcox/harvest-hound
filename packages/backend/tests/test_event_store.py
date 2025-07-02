import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.events.domain_events import InventoryItemAdded, StoreCreated
from app.infrastructure.event_store import EventStore


class TestEventStoreAppendEvent:
    """Test EventStore.append_event() persists events to SQLite."""

    def test_append_event_persists_store_created_event(self):
        """EventStore.append_event() should persist StoreCreated event to SQLite."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Create event store and event
            event_store = EventStore(db_path)
            store_id = uuid4()
            stream_id = f"store-{store_id}"

            event = StoreCreated(
                store_id=store_id,
                name="Test Store",
                description="A test store",
                infinite_supply=False,
                created_at=datetime.now(),
            )

            # Append event
            event_store.append_event(stream_id, event)

            # Verify event was persisted by loading it back
            loaded_events = event_store.load_events(stream_id)

            assert len(loaded_events) == 1
            loaded_event = loaded_events[0]
            assert loaded_event["event_type"] == "StoreCreated"
            assert loaded_event["event_data"]["store_id"] == str(store_id)
            assert loaded_event["event_data"]["name"] == "Test Store"
            assert loaded_event["event_data"]["description"] == "A test store"
            assert loaded_event["event_data"]["infinite_supply"] is False

        finally:
            # Clean up
            Path(db_path).unlink(missing_ok=True)


class TestEventStoreLoadEvents:
    """Test EventStore.load_events() returns events in chronological order."""

    def test_load_events_returns_events_in_chronological_order(self):
        """EventStore should return events by stream_id in chronological order."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            event_store = EventStore(db_path)
            store_id = uuid4()
            ingredient_id = uuid4()
            stream_id = f"store-{store_id}"

            # Create events with slight time delays to ensure ordering
            event1 = StoreCreated(
                store_id=store_id,
                name="Test Store",
                description="A test store",
                infinite_supply=False,
                created_at=datetime.now(),
            )

            time.sleep(0.001)  # Ensure different timestamps

            event2 = InventoryItemAdded(
                store_id=store_id,
                ingredient_id=ingredient_id,
                quantity=2.0,
                unit="lbs",
                notes="First item",
                added_at=datetime.now(),
            )

            time.sleep(0.001)  # Ensure different timestamps

            event3 = InventoryItemAdded(
                store_id=store_id,
                ingredient_id=ingredient_id,
                quantity=1.0,
                unit="bunch",
                notes="Second item",
                added_at=datetime.now(),
            )

            # Append events
            event_store.append_event(stream_id, event1)
            event_store.append_event(stream_id, event2)
            event_store.append_event(stream_id, event3)

            # Load events
            loaded_events = event_store.load_events(stream_id)

            # Verify order and content
            assert len(loaded_events) == 3
            assert loaded_events[0]["event_type"] == "StoreCreated"
            assert loaded_events[1]["event_type"] == "InventoryItemAdded"
            assert loaded_events[1]["event_data"]["notes"] == "First item"
            assert loaded_events[2]["event_type"] == "InventoryItemAdded"
            assert loaded_events[2]["event_data"]["notes"] == "Second item"

            # Verify chronological ordering by timestamp
            timestamps = [event["timestamp"] for event in loaded_events]
            assert timestamps == sorted(timestamps)

        finally:
            # Clean up
            Path(db_path).unlink(missing_ok=True)


class TestEventStoreConcurrentWrites:
    """Test EventStore handles concurrent writes without corruption."""

    def test_concurrent_writes_no_corruption(self):
        """EventStore should handle concurrent writes without corruption."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            event_store = EventStore(db_path)

            # Create multiple threads that write events concurrently
            def write_events(thread_id):
                for i in range(10):
                    store_id = uuid4()
                    stream_id = f"store-{store_id}"
                    event = StoreCreated(
                        store_id=store_id,
                        name=f"Store-{thread_id}-{i}",
                        description=f"Store from thread {thread_id}, iteration {i}",
                        infinite_supply=False,
                        created_at=datetime.now(),
                    )
                    event_store.append_event(stream_id, event)

            # Run concurrent writes
            threads = []
            num_threads = 5
            for thread_id in range(num_threads):
                thread = threading.Thread(target=write_events, args=(thread_id,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all events were written (5 threads * 10 events each = 50 total)
            # We'll check by examining the database directly
            import sqlite3

            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM events")
                count = cursor.fetchone()[0]
                assert count == 50

            # Verify no data corruption by checking a few random events
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute(
                    "SELECT event_type, event_data FROM events LIMIT 5"
                )
                for row in cursor.fetchall():
                    event_type, event_data = row
                    assert event_type == "StoreCreated"
                    # Should be valid JSON
                    import json

                    parsed_data = json.loads(event_data)
                    assert "store_id" in parsed_data
                    assert "name" in parsed_data

        finally:
            # Clean up
            Path(db_path).unlink(missing_ok=True)
