#!/usr/bin/env python3
"""
Export Pydantic models to JSON Schema for TypeScript generation.
This makes the backend the source of truth for all data types.
"""

import json
from pathlib import Path
from typing import Any, Dict, Type

from pydantic import BaseModel

from app.events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from app.models.ingredient import Ingredient
from app.models.inventory_item import InventoryItem
from app.models.inventory_store import InventoryStore


def export_model_schema(model_class: Type[BaseModel], title: str | None = None) -> Dict[str, Any]:
    """Export a Pydantic model to JSON Schema."""
    # Generate schema with mode that avoids complex types
    schema = model_class.model_json_schema(mode="serialization")
    if title:
        schema["title"] = title

    # Inline any $defs references to avoid external dependencies
    if "$defs" in schema:
        defs = schema.pop("$defs")
        schema = _inline_refs(schema, defs)

    # Simplify the schema by removing title constraints that create type aliases
    schema = _simplify_schema(schema)

    return schema  # type: ignore[no-any-return]


def _simplify_schema(obj: Any) -> Any:
    """Simplify schema by removing titles that create unnecessary type aliases."""
    if isinstance(obj, dict):
        # Create a copy to avoid modifying the original
        result = {}
        for k, v in obj.items():
            # Skip titles for simple types and anyOf patterns to prevent aliases
            if k == "title":
                if isinstance(obj.get("type"), str) and obj.get("type") in [
                    "string",
                    "number",
                    "boolean",
                    "array",
                    "object",
                ]:
                    continue
                elif "anyOf" in obj:
                    # Skip title for anyOf patterns (like optional fields)
                    continue
            result[k] = _simplify_schema(v)
        return result
    elif isinstance(obj, list):
        return [_simplify_schema(item) for item in obj]
    else:
        return obj


def _inline_refs(obj: Any, defs: Dict[str, Any]) -> Any:
    """Recursively inline $ref pointers."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_path = obj["$ref"]
            if ref_path.startswith("#"):
                # Extract the definition name
                ref_name = ref_path.split("/")[-1] if "/" in ref_path else ref_path[1:]
                if ref_name in defs:
                    # Recursively inline the referenced definition
                    return _inline_refs(defs[ref_name], defs)
            return obj
        else:
            return {k: _inline_refs(v, defs) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_inline_refs(item, defs) for item in obj]
    else:
        return obj


def main() -> None:
    """Export all models to a combined JSON Schema file."""

    # Core domain models
    schemas = {
        "Ingredient": export_model_schema(Ingredient),
        "InventoryItem": export_model_schema(InventoryItem),
        "InventoryStore": export_model_schema(InventoryStore),
        # Events
        "IngredientCreated": export_model_schema(IngredientCreated),
        "StoreCreated": export_model_schema(StoreCreated),
        "InventoryItemAdded": export_model_schema(InventoryItemAdded),
    }

    # Create combined schema with definitions
    combined_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Harvest Hound API Types",
        "type": "object",
        "definitions": schemas,
    }

    # Ensure output directory exists
    output_dir = Path(__file__).parent.parent / "generated"
    output_dir.mkdir(exist_ok=True)

    # Write schema file
    schema_file = output_dir / "api-types.json"
    with open(schema_file, "w") as f:
        json.dump(combined_schema, f, indent=2, default=str)

    print(f"✅ Exported schemas to {schema_file}")
    print(f"📊 Exported {len(schemas)} model schemas")

    # List exported models
    for name in schemas.keys():
        print(f"   - {name}")


if __name__ == "__main__":
    main()
