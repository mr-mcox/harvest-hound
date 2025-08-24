"""Test implementations of inventory parser protocols."""

from typing import Dict, List, Optional

from app.models.parsed_inventory import ParsedInventoryItem


class MockInventoryParser:
    """Mock inventory parser with configurable responses."""

    def __init__(self, responses: Optional[Dict[str, List[ParsedInventoryItem]]] = None) -> None:
        """Initialize with optional response map.
        
        Args:
            responses: Map of input text to expected parsed items
        """
        self.responses = responses or {}
        self._call_count = 0

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using pre-configured responses."""
        self._call_count += 1
        
        if not inventory_text.strip():
            return []
            
        # Return configured response if available
        if inventory_text in self.responses:
            return self.responses[inventory_text]
            
        # Default fixture-based responses for common test cases
        default_fixtures = {
            "2 lbs carrots, 1 bunch kale": [
                ParsedInventoryItem(name="carrot", quantity=2.0, unit="pound"),
                ParsedInventoryItem(name="kale", quantity=1.0, unit="bunch"),
            ],
            "3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil": [
                ParsedInventoryItem(name="spinach", quantity=3.5, unit="ounce"),
                ParsedInventoryItem(name="milk", quantity=2.25, unit="cup"),
                ParsedInventoryItem(name="olive oil", quantity=0.5, unit="cup"),
            ],
            "1 apple": [
                ParsedInventoryItem(name="apple", quantity=1.0, unit="piece"),
            ],
        }
        
        return default_fixtures.get(inventory_text, [])

    @property
    def call_count(self) -> int:
        """Get number of times parse_inventory was called."""
        return self._call_count


class FailingMockInventoryParser:
    """Mock parser that simulates various failure scenarios."""

    def __init__(self, error_type: str = "parsing") -> None:
        """Initialize with error type.
        
        Args:
            error_type: Type of error to simulate ("parsing", "timeout", "network")
        """
        self.error_type = error_type

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Simulate parsing failures."""
        if self.error_type == "timeout":
            raise TimeoutError("LLM service timeout")
        elif self.error_type == "parsing":
            raise ValueError("Failed to parse inventory text")
        elif self.error_type == "network":
            raise ConnectionError("Network error connecting to LLM service")
        else:
            raise RuntimeError(f"Unknown error type: {self.error_type}")


class ConfigurableMockInventoryParser:
    """Mock parser with runtime configuration support."""

    def __init__(self) -> None:
        """Initialize with empty configuration."""
        self._responses: Dict[str, List[ParsedInventoryItem]] = {}
        self._should_fail = False
        self._failure_error: Optional[Exception] = None

    def set_response(self, input_text: str, parsed_items: List[ParsedInventoryItem]) -> None:
        """Configure response for specific input.
        
        Args:
            input_text: Input text to match
            parsed_items: Items to return for this input
        """
        self._responses[input_text] = parsed_items

    def set_failure(self, error: Exception) -> None:
        """Configure parser to fail with specific error.
        
        Args:
            error: Exception to raise on next call
        """
        self._should_fail = True
        self._failure_error = error

    def clear_failure(self) -> None:
        """Clear failure configuration."""
        self._should_fail = False
        self._failure_error = None

    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory using configured responses or failures."""
        if self._should_fail and self._failure_error:
            raise self._failure_error
            
        if not inventory_text.strip():
            return []
            
        return self._responses.get(inventory_text, [])