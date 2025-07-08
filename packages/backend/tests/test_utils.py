"""Shared test utilities for event-based testing."""

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Type

from app.infrastructure.event_store import EventStore


def get_typed_events(
    event_store: EventStore, stream_id: str, event_type_class: Type[Any]
) -> List[Any]:
    """Get typed domain events from event store.

    Args:
        event_store: The event store to load from
        stream_id: Stream identifier to load events from
        event_type_class: Domain event class to filter and convert to

    Returns:
        List of typed domain event objects
    """
    raw_events = event_store.load_events(stream_id)
    return [
        event_type_class(**event["event_data"])
        for event in raw_events
        if event["event_type"] == event_type_class.__name__
    ]


def assert_event_matches(
    event: Any,
    expected_data: Optional[Dict[str, Any]] = None,
    exclude_fields: Optional[List[str]] = None,
) -> None:
    """Assert a typed domain event matches expected data.

    Args:
        event: Typed domain event object
        expected_data: Dict of field->value pairs to check (optional)
        exclude_fields: List of fields to skip (defaults to timestamp fields)

    Example:
        assert_event_matches(store_event, {
            "name": "CSA Box",
            "infinite_supply": False
        })
    """
    exclude_fields = exclude_fields or ["created_at", "added_at"]

    if expected_data:
        # Convert event to dict (works for both pydantic and dataclass)
        if hasattr(event, "model_dump"):
            actual_data = event.model_dump()
        else:
            actual_data = asdict(event)

        # Filter out excluded fields
        actual_data = {k: v for k, v in actual_data.items() if k not in exclude_fields}

        # Only check the fields that were specified
        for field, expected_value in expected_data.items():
            assert field in actual_data, f"Field '{field}' not found in event data"
            assert (
                actual_data[field] == expected_value
            ), f"Field '{field}': expected {expected_value}, got {actual_data[field]}"
