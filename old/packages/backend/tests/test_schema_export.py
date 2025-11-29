"""Tests for schema export service."""

import json
import tempfile
from pathlib import Path
from typing import Optional

import pytest
from pydantic import BaseModel

from app.services.schema_export import SchemaExportService


class SimpleTestModel(BaseModel):
    """Simple model for testing schema export."""

    name: str
    count: int
    description: Optional[str] = None


class TestSchemaExportService:
    """Test the schema export service."""

    @pytest.fixture
    def export_service(self) -> SchemaExportService:
        """Create a schema export service for testing."""
        return SchemaExportService()

    def test_export_model_schema_generates_valid_json_schema(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that exporting a model generates valid JSON Schema."""
        schema = export_service.export_model_schema(SimpleTestModel)

        # Should be a valid JSON Schema
        assert isinstance(schema, dict)
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema

        # Should have all model fields
        properties = schema["properties"]
        assert "name" in properties
        assert "count" in properties
        assert "description" in properties

        # Required fields should be marked as required
        assert "required" in schema
        assert "name" in schema["required"]
        assert "count" in schema["required"]
        assert "description" not in schema["required"]  # Optional field

    def test_export_model_schema_with_custom_title(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that custom title is applied to schema."""
        custom_title = "CustomModelTitle"
        schema = export_service.export_model_schema(SimpleTestModel, title=custom_title)

        assert schema["title"] == custom_title

    def test_export_all_schemas_includes_all_registered_models(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that export_all_schemas includes all registered models."""
        schemas = export_service.export_all_schemas()

        # Should include core domain models
        assert "Ingredient" in schemas
        assert "InventoryItem" in schemas
        assert "InventoryStore" in schemas

        # Should include read models from ADR-005
        assert "InventoryItemView" in schemas
        assert "StoreView" in schemas

        # Should include domain events
        assert "IngredientCreated" in schemas
        assert "StoreCreated" in schemas
        assert "InventoryItemAdded" in schemas

        # Each schema should be a valid JSON Schema object
        for name, schema in schemas.items():
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "properties" in schema

    def test_create_combined_schema_has_correct_structure(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that combined schema has the correct JSON Schema structure."""
        schemas = {
            "TestModel": {"type": "object", "properties": {"field": {"type": "string"}}}
        }
        combined = export_service.create_combined_schema(schemas)

        assert combined["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert combined["title"] == "Harvest Hound API Types"
        assert combined["type"] == "object"
        assert combined["definitions"] == schemas

    def test_write_schema_file_creates_valid_json_file(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that writing schema creates a valid JSON file."""
        schema = {"test": "data", "number": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test-schema.json"
            export_service.write_schema_file(schema, output_path)

            # File should exist
            assert output_path.exists()

            # File should contain valid JSON matching our schema
            with open(output_path) as f:
                loaded_schema = json.load(f)

            assert loaded_schema == schema

    def test_write_schema_file_creates_output_directory(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that write_schema_file creates parent directories if they don't
        exist.
        """
        schema = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "directory" / "schema.json"
            export_service.write_schema_file(schema, output_path)

            # File and directories should exist
            assert output_path.exists()
            assert output_path.parent.exists()

    def test_export_to_file_complete_workflow(
        self, export_service: SchemaExportService
    ) -> None:
        """Test the complete export workflow from models to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "api-types.json"
            exported_models = export_service.export_to_file(output_path)

            # Should return list of exported model names
            assert isinstance(exported_models, list)
            assert len(exported_models) > 0
            assert "Ingredient" in exported_models
            assert "InventoryItemView" in exported_models

            # File should exist and contain valid JSON
            assert output_path.exists()
            with open(output_path) as f:
                schema_data = json.load(f)

            # Should have correct structure
            assert schema_data["$schema"] == "http://json-schema.org/draft-07/schema#"
            assert "definitions" in schema_data
            assert len(schema_data["definitions"]) == len(exported_models)

            # Each exported model should have a valid schema
            for model_name in exported_models:
                assert model_name in schema_data["definitions"]
                model_schema = schema_data["definitions"][model_name]
                assert "type" in model_schema
                assert "properties" in model_schema

    def test_schema_includes_read_models_from_adr_005(
        self, export_service: SchemaExportService
    ) -> None:
        """Test that exported schemas include the new read models from ADR-005."""
        schemas = export_service.export_all_schemas()

        # Verify InventoryItemView schema
        inventory_view_schema = schemas["InventoryItemView"]
        properties = inventory_view_schema["properties"]

        # Should have denormalized fields
        assert "ingredient_name" in properties
        assert "store_name" in properties
        assert "store_id" in properties
        assert "ingredient_id" in properties
        assert "quantity" in properties
        assert "unit" in properties

        # Verify StoreView schema
        store_view_schema = schemas["StoreView"]
        store_properties = store_view_schema["properties"]

        # Should have computed fields
        assert "item_count" in store_properties
        assert "store_id" in store_properties
        assert "name" in store_properties
