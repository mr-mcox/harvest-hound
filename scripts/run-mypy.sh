#!/bin/bash
set -e

# Get the project root directory (where this script is called from)
PROJECT_ROOT="$(pwd)"

# Change to the backend directory
cd packages/backend

# Check if any arguments (files) were passed
if [ $# -eq 0 ]; then
    # No files specified, run mypy on the entire app directory
    uv run mypy --config-file pyproject.toml app/
else
    # Filter arguments to only include Python files in the backend
    python_files=()
    for file in "$@"; do
        # Convert relative paths from project root to backend-relative paths
        if [[ "$file" == packages/backend/* ]]; then
            # Remove the packages/backend/ prefix
            backend_file="${file#packages/backend/}"
            # Only include Python files
            if [[ "$backend_file" == *.py ]]; then
                python_files+=("$backend_file")
            fi
        fi
    done

    # Run mypy on the filtered files if any exist
    if [ ${#python_files[@]} -gt 0 ]; then
        uv run mypy --config-file pyproject.toml "${python_files[@]}"
    else
        # No Python files to check, exit successfully
        echo "No Python files to type check"
        exit 0
    fi
fi
