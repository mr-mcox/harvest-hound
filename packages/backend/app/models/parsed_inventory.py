from dataclasses import dataclass


@dataclass
class ParsedInventoryItem:
    """Domain model for parsed inventory items from text input.

    This represents the result of parsing natural language text into
    structured inventory data before creating domain aggregates.
    """

    name: str
    quantity: float
    unit: str

    def __post_init__(self) -> None:
        """Validate domain constraints."""
        if not self.name or not self.name.strip():
            raise ValueError("Ingredient name cannot be empty")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if not self.unit or not self.unit.strip():
            raise ValueError("Unit cannot be empty")
