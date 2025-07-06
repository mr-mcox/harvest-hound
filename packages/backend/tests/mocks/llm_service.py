"""Mock LLM service for predictable testing of inventory parsing."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.parsed_inventory import ParsedInventoryItem
from app.services.inventory_parser import InventoryParserClient


class MockLLMInventoryParser(InventoryParserClient):
    """Mock LLM service that returns deterministic responses based on fixtures."""

    def __init__(
        self,
        fixtures_path: Optional[Path] = None,
        failure_mode: Optional[str] = None,
        simulate_timing: bool = False,
    ):
        """Initialize mock LLM service.
        
        Args:
            fixtures_path: Path to LLM response fixtures JSON file
            failure_mode: Type of failure to simulate (timeout, error, partial)
            simulate_timing: Whether to simulate response latency
        """
        self.fixtures_path = fixtures_path or (
            Path(__file__).parent.parent / "fixtures" / "llm_responses.json"
        )
        self.failure_mode = failure_mode
        self.simulate_timing = simulate_timing
        
        # Load fixtures
        with open(self.fixtures_path) as f:
            self.fixtures = json.load(f)
    
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Parse inventory text using fixture-based responses."""
        if not inventory_text.strip():
            return []
        
        # Simulate failure modes
        if self.failure_mode == "timeout":
            time.sleep(2.0)  # Simulate timeout
            raise TimeoutError("LLM service timeout")
        elif self.failure_mode == "error":
            raise RuntimeError("LLM service error")
        elif self.failure_mode == "parsing_error":
            raise ValueError("Failed to parse LLM response")
        
        # Find matching fixture
        response_data = self._find_matching_fixture(inventory_text)
        
        # Simulate timing if requested
        if self.simulate_timing and "simulated_latency_ms" in response_data:
            latency = response_data["simulated_latency_ms"] / 1000.0
            time.sleep(latency)
        
        # Convert fixture data to domain objects
        output = response_data.get("output", [])
        return [
            ParsedInventoryItem(
                name=item["name"],
                quantity=item["quantity"],
                unit=item["unit"]
            )
            for item in output
        ]
    
    def _find_matching_fixture(self, inventory_text: str) -> Dict[str, Any]:
        """Find fixture that matches the input text."""
        # First try exact matches
        for category in self.fixtures.values():
            if not isinstance(category, dict):
                continue
            for scenario_name, scenario_data in category.items():
                if isinstance(scenario_data, dict) and scenario_data.get("input") == inventory_text:
                    return scenario_data
        
        # Then try pattern matching for common cases
        text_lower = inventory_text.lower()
        
        # Empty/whitespace
        if not inventory_text.strip():
            return self.fixtures["edge_cases"]["empty_input"]  # type: ignore[no-any-return]
        
        # Single item
        if len(inventory_text.split(",")) == 1 and "apple" in text_lower:
            return self.fixtures["edge_cases"]["single_item"]  # type: ignore[no-any-return]
        
        # Default to simple items for basic parsing
        if any(word in text_lower for word in ["carrot", "kale"]):
            return self.fixtures["successful_parsing"]["simple_items"]  # type: ignore[no-any-return]
        
        # Unicode or special characters
        if any(char for char in inventory_text if ord(char) > 127):
            return self.fixtures["edge_cases"]["unicode_characters"]  # type: ignore[no-any-return]
        
        # Very long lists (rough heuristic)
        if len(inventory_text.split(",")) > 5:
            return self.fixtures["edge_cases"]["very_long_list"]  # type: ignore[no-any-return]
        
        # Default to parsing failure for unrecognized input
        return self.fixtures["parsing_failures"]["complete_failure"]  # type: ignore[no-any-return]
    
    def configure_response(self, input_text: str, output_items: List[Dict[str, Any]]) -> None:
        """Configure a specific response for testing.
        
        Args:
            input_text: Input text to match
            output_items: List of dicts with name, quantity, unit keys
        """
        # Add custom fixture for this test
        if "custom" not in self.fixtures:
            self.fixtures["custom"] = {}
        
        self.fixtures["custom"][f"test_input_{len(self.fixtures['custom'])}"] = {
            "input": input_text,
            "output": output_items
        }


class ConfigurableMockLLMParser(InventoryParserClient):
    """Simple mock for direct test configuration without fixtures."""
    
    def __init__(self, responses: Optional[Dict[str, List[ParsedInventoryItem]]] = None):
        """Initialize with pre-configured responses.
        
        Args:
            responses: Dict mapping input text to list of ParsedInventoryItem
        """
        self.responses = responses or {}
        self.default_response: List[ParsedInventoryItem] = []
    
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Return configured response for input text."""
        if not inventory_text.strip():
            return []
        
        return self.responses.get(inventory_text, self.default_response)
    
    def set_response(self, input_text: str, items: List[ParsedInventoryItem]) -> None:
        """Set response for specific input text."""
        self.responses[input_text] = items
    
    def set_default_response(self, items: List[ParsedInventoryItem]) -> None:
        """Set default response for any unmatched input."""
        self.default_response = items


class FailingMockLLMParser(InventoryParserClient):
    """Mock that always fails for error testing."""
    
    def __init__(self, error_type: str = "runtime"):
        """Initialize with specific error type.
        
        Args:
            error_type: Type of error (runtime, timeout, parsing)
        """
        self.error_type = error_type
    
    def parse_inventory(self, inventory_text: str) -> List[ParsedInventoryItem]:
        """Always raise an error."""
        if self.error_type == "timeout":
            raise TimeoutError("LLM service timeout")
        elif self.error_type == "parsing":
            raise ValueError("Failed to parse LLM response")
        else:
            raise RuntimeError("LLM service error")