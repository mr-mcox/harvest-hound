#!/usr/bin/env python3
"""
Export Pydantic models to JSON Schema for TypeScript generation.
This makes the backend the source of truth for all data types.

This is a simple wrapper around the SchemaExportService.
"""

import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.schema_export import SchemaExportService


def main() -> None:
    """Export all models to a combined JSON Schema file."""
    service = SchemaExportService()

    # Determine output path
    output_dir = Path(__file__).parent.parent / "generated"
    schema_file = output_dir / "api-types.json"

    # Export schemas
    exported_models = service.export_to_file(schema_file)

    # Report results
    print(f"✅ Exported schemas to {schema_file}")
    print(f"📊 Exported {len(exported_models)} model schemas")

    # List exported models
    for name in exported_models:
        print(f"   - {name}")


if __name__ == "__main__":
    main()
