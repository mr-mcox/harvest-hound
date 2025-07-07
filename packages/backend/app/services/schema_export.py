"""
Schema export service for generating TypeScript types from Pydantic models.

This service provides the core functionality for exporting backend schemas
to JSON Schema format, enabling type-safe frontend integration.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel

from ..events.domain_events import IngredientCreated, InventoryItemAdded, StoreCreated
from ..models.ingredient import Ingredient
from ..models.inventory_item import InventoryItem
from ..models.inventory_store import InventoryStore
from ..models.read_models import InventoryItemView, StoreView


class SchemaExportService:
    """Service for exporting Pydantic models to JSON Schema."""
    
    def __init__(self) -> None:
        """Initialize the schema export service."""
        self._models_to_export = [
            # Core domain models
            ("Ingredient", Ingredient),
            ("InventoryItem", InventoryItem),
            ("InventoryStore", InventoryStore),
            # Read models (ADR-005)
            ("InventoryItemView", InventoryItemView),
            ("StoreView", StoreView),
            # Domain events
            ("IngredientCreated", IngredientCreated),
            ("StoreCreated", StoreCreated),
            ("InventoryItemAdded", InventoryItemAdded),
        ]
    
    def export_model_schema(self, model_class: Type[BaseModel], title: str | None = None) -> Dict[str, Any]:
        """Export a Pydantic model to JSON Schema."""
        # Generate schema with mode that avoids complex types
        schema = model_class.model_json_schema(mode="serialization")
        if title:
            schema["title"] = title

        # Inline any $defs references to avoid external dependencies
        if "$defs" in schema:
            defs = schema.pop("$defs")
            schema = self._inline_refs(schema, defs)

        # Simplify the schema by removing title constraints that create type aliases
        schema = self._simplify_schema(schema)

        return schema  # type: ignore[no-any-return]
    
    def export_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Export all registered models to JSON Schema format."""
        schemas = {}
        
        for name, model_class in self._models_to_export:
            schemas[name] = self.export_model_schema(model_class)
        
        return schemas
    
    def create_combined_schema(self, schemas: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a combined JSON Schema with all model definitions."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Harvest Hound API Types",
            "type": "object",
            "definitions": schemas,
        }
    
    def write_schema_file(self, schema: Dict[str, Any], output_path: Path) -> None:
        """Write schema to file with proper formatting."""
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write schema file
        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2, default=str)
    
    def export_to_file(self, output_path: Path) -> List[str]:
        """
        Export all schemas to a JSON file and return list of exported model names.
        
        Returns:
            List of exported model names for reporting
        """
        schemas = self.export_all_schemas()
        combined_schema = self.create_combined_schema(schemas)
        self.write_schema_file(combined_schema, output_path)
        
        return list(schemas.keys())
    
    def _simplify_schema(self, obj: Any, is_root: bool = True) -> Any:
        """Simplify schema by removing titles that create unnecessary type aliases."""
        if isinstance(obj, dict):
            # Create a copy to avoid modifying the original
            result = {}
            for k, v in obj.items():
                # Keep title for root level schemas, but skip for nested simple types
                if k == "title" and not is_root:
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
                result[k] = self._simplify_schema(v, is_root=False)
            return result
        elif isinstance(obj, list):
            return [self._simplify_schema(item, is_root=False) for item in obj]
        else:
            return obj

    def _inline_refs(self, obj: Any, defs: Dict[str, Any]) -> Any:
        """Recursively inline $ref pointers."""
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_path = obj["$ref"]
                if ref_path.startswith("#"):
                    # Extract the definition name
                    ref_name = ref_path.split("/")[-1] if "/" in ref_path else ref_path[1:]
                    if ref_name in defs:
                        # Recursively inline the referenced definition
                        return self._inline_refs(defs[ref_name], defs)
                return obj
            else:
                return {k: self._inline_refs(v, defs) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._inline_refs(item, defs) for item in obj]
        else:
            return obj