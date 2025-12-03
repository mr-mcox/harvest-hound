#!/usr/bin/env python3
"""
Round-trip fidelity test for pitch-recipe relationship.

Tests: Original Recipe → Generate Pitch → Flesh Out → Judge Fidelity

This measures whether the LLM can maintain recipe character and identity
through the pitch generation and flesh-out cycle.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

from baml_client import b
from baml_client.types import FidelityScore, Recipe, RecipePitch

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


# Test recipes with distinctive character
TEST_RECIPES = [
    "Kimchi Carbonara_176468579537173.yml",
    "Spaghetti All'Assassina_176468579620041.yml",
    "Chicken Yassa (Senegalese Braised Chicke_176468579774694.yml",
    "Baasto iyo Suugo Tuuna (Pasta and Spiced_176468579675206.yml",
]


def load_recipe_yaml(filename: str) -> dict:
    """Load a recipe from the exported YAML files."""
    recipe_dir = (
        Path(__file__).parent.parent.parent
        / ".scratch"
        / "CookBook-Recipes-YAML-20251202T0829579140600"
    )
    filepath = recipe_dir / filename

    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def format_ingredients(ingredients: list) -> str:
    """Format ingredient list as readable string."""
    if not ingredients:
        return ""

    formatted = []
    for ing in ingredients:
        if isinstance(ing, str):
            formatted.append(f"- {ing}")
        else:
            # Handle dict format if present
            formatted.append(f"- {ing}")
    return "\n".join(formatted)


def format_directions(directions: list) -> str:
    """Format directions list as readable string."""
    if not directions:
        return ""

    # Filter out empty strings and join
    steps = [step for step in directions if step.strip()]
    return "\n\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps))


def format_recipe_ingredients_for_generation(pitch: RecipePitch) -> str:
    """Format pitch ingredients for passing to recipe generation."""
    ingredients = []
    for ing in pitch.key_ingredients:
        ingredients.append(ing)
    return ", ".join(ingredients)


async def test_single_recipe(recipe_filename: str) -> dict:
    """Run round-trip test on a single recipe."""
    print(f"\n{'=' * 80}")
    print(f"Testing: {recipe_filename}")
    print("=" * 80)

    # Load original recipe
    original = load_recipe_yaml(recipe_filename)

    print(f"\n[ORIGINAL] {original['name']}")
    if "description" in original and original["description"]:
        print(f"Description: {original['description'][:200]}...")

    # Step 1: Generate pitch from original recipe
    print("\n[STEP 1] Generating pitch from original recipe...")

    ingredients_str = format_ingredients(original.get("ingredients", []))
    directions_str = format_directions(original.get("directions", []))
    description_str = original.get("description", "")

    pitch = await b.GeneratePitchFromRecipe(
        recipe_name=original["name"],
        recipe_ingredients=ingredients_str,
        recipe_instructions=directions_str,
        recipe_description=description_str,
    )

    print(f"\n[PITCH GENERATED]")
    print(f"  Name: {pitch.name}")
    print(f"  Blurb: {pitch.blurb}")
    print(f"  Why: {pitch.why_make_this}")
    print(f"  Key ingredients: {', '.join(pitch.key_ingredients)}")
    print(f"  Time: {pitch.active_time_minutes} min")

    # Step 2: Generate recipe from pitch
    print("\n[STEP 2] Generating recipe from pitch...")

    # Create context string that includes the pitch information
    pitch_context = f"""Generate a recipe for: {pitch.name}

Pitch description: {pitch.blurb}

Why make this: {pitch.why_make_this}

Should feature these key ingredients: {", ".join(pitch.key_ingredients)}

Active time should be approximately: {pitch.active_time_minutes} minutes
"""

    # For this test, we'll provide all ingredients as available from a test store
    key_ingredients_list = ", ".join(pitch.key_ingredients)
    explicit_stores = f"Test Store: {key_ingredients_list}"
    definition_stores = "Pantry: salt, pepper, oil, butter, flour, sugar, common spices"

    generated = await b.GenerateSingleRecipe(
        explicit_stores=explicit_stores,
        definition_stores=definition_stores,
        additional_context=pitch_context,
        recipes_already_generated="",
    )

    print(f"\n[RECIPE GENERATED]")
    print(f"  Name: {generated.name}")
    print(f"  Ingredients: {len(generated.ingredients)} items")
    print(f"  Instructions length: {len(generated.instructions)} chars")
    print(
        f"  Time: {generated.active_time_minutes} active + {generated.passive_time_minutes or 0} passive"
    )

    # Step 3: Judge fidelity
    print("\n[STEP 3] Judging fidelity...")

    generated_ingredients_str = "\n".join(
        [f"- {ing.quantity} {ing.unit} {ing.name}" for ing in generated.ingredients]
    )

    fidelity = await b.JudgeFidelity(
        original_recipe_name=original["name"],
        original_recipe_description=description_str,
        original_ingredients=ingredients_str,
        original_instructions=directions_str,
        pitch_name=pitch.name,
        pitch_blurb=pitch.blurb,
        pitch_why_make_this=pitch.why_make_this,
        generated_recipe_name=generated.name,
        generated_ingredients=generated_ingredients_str,
        generated_instructions=generated.instructions,
    )

    print(f"\n[FIDELITY SCORES]")
    print(f"  Ingredient Alignment: {fidelity.ingredient_alignment}/100")
    print(f"    → {fidelity.ingredient_reasoning}")
    print(f"  Effort Alignment: {fidelity.effort_alignment}/100")
    print(f"    → {fidelity.effort_reasoning}")
    print(f"  Experience Alignment: {fidelity.experience_alignment}/100")
    print(f"    → {fidelity.experience_reasoning}")
    print(f"  Character Preservation: {fidelity.character_preservation}/100")
    print(f"    → {fidelity.character_reasoning}")
    print(f"\n  OVERALL: {fidelity.overall_score}/100")
    print(f"  {fidelity.overall_assessment}")

    return {
        "recipe_name": original["name"],
        "filename": recipe_filename,
        "original_recipe": {
            "name": original["name"],
            "description": original.get("description", ""),
            "ingredients": original.get("ingredients", []),
            "directions": original.get("directions", []),
        },
        "pitch": {
            "name": pitch.name,
            "blurb": pitch.blurb,
            "why_make_this": pitch.why_make_this,
            "key_ingredients": pitch.key_ingredients,
            "active_time_minutes": pitch.active_time_minutes,
        },
        "generated_recipe": {
            "name": generated.name,
            "ingredients": [
                {"name": ing.name, "quantity": ing.quantity, "unit": ing.unit}
                for ing in generated.ingredients
            ],
            "instructions": generated.instructions,
            "active_time_minutes": generated.active_time_minutes,
            "passive_time_minutes": generated.passive_time_minutes,
            "servings": generated.servings,
            "notes": generated.notes,
        },
        "fidelity": {
            "ingredient_alignment": fidelity.ingredient_alignment,
            "ingredient_reasoning": fidelity.ingredient_reasoning,
            "effort_alignment": fidelity.effort_alignment,
            "effort_reasoning": fidelity.effort_reasoning,
            "experience_alignment": fidelity.experience_alignment,
            "experience_reasoning": fidelity.experience_reasoning,
            "character_preservation": fidelity.character_preservation,
            "character_reasoning": fidelity.character_reasoning,
            "overall_score": fidelity.overall_score,
            "overall_assessment": fidelity.overall_assessment,
        },
    }


async def run_all_tests():
    """Run tests on all selected recipes."""
    # Set up output file
    output_dir = Path(__file__).parent.parent.parent / ".scratch"
    output_file = (
        output_dir
        / f"fidelity-test-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    )

    def log(msg):
        """Print and save to file."""
        print(msg)
        with open(output_file, "a") as f:
            f.write(msg + "\n")

    log(f"\n{'#' * 80}")
    log("# PITCH-RECIPE FIDELITY TEST")
    log(f"# Testing {len(TEST_RECIPES)} recipes with distinctive character")
    log(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"# Results saved to: {output_file}")
    log("#" * 80)

    results = []

    for recipe_file in TEST_RECIPES:
        try:
            result = await test_single_recipe(recipe_file)
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR testing {recipe_file}: {e}")
            import traceback

            traceback.print_exc()
            results.append(
                {"recipe_name": recipe_file, "filename": recipe_file, "error": str(e)}
            )

    # Summary
    print(f"\n\n{'#' * 80}")
    print("# SUMMARY")
    print("#" * 80)

    successful_tests = [r for r in results if "fidelity" in r]
    failed_tests = [r for r in results if "error" in r]

    print(f"\nTests run: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")

    if successful_tests:
        print(
            f"\n{'Recipe':<50} {'Overall':>8} {'Ingr':>6} {'Effort':>6} {'Exp':>6} {'Char':>6}"
        )
        print("-" * 94)

        for result in successful_tests:
            f = result["fidelity"]
            name = (
                result["recipe_name"][:47] + "..."
                if len(result["recipe_name"]) > 50
                else result["recipe_name"]
            )
            print(
                f"{name:<50} {f['overall_score']:>7}/100 {f['ingredient_alignment']:>5}/100 {f['effort_alignment']:>5}/100 {f['experience_alignment']:>5}/100 {f['character_preservation']:>5}/100"
            )

        # Calculate averages
        avg_overall = sum(
            r["fidelity"]["overall_score"] for r in successful_tests
        ) / len(successful_tests)
        avg_ingredient = sum(
            r["fidelity"]["ingredient_alignment"] for r in successful_tests
        ) / len(successful_tests)
        avg_effort = sum(
            r["fidelity"]["effort_alignment"] for r in successful_tests
        ) / len(successful_tests)
        avg_experience = sum(
            r["fidelity"]["experience_alignment"] for r in successful_tests
        ) / len(successful_tests)
        avg_character = sum(
            r["fidelity"]["character_preservation"] for r in successful_tests
        ) / len(successful_tests)

        print("-" * 94)
        print(
            f"{'AVERAGE':<50} {avg_overall:>7.1f}/100 {avg_ingredient:>5.1f}/100 {avg_effort:>5.1f}/100 {avg_experience:>5.1f}/100 {avg_character:>5.1f}/100"
        )

        print(f"\n{'=' * 80}")
        print("INTERPRETATION")
        print("=" * 80)

        if avg_overall >= 90:
            print(
                "✓ HIGH FIDELITY (90+): Current prompts maintain recipe identity well."
            )
            print("  → No immediate architectural changes needed")
            print("  → Can proceed with current approach")
        elif avg_overall >= 70:
            print("⚠ MEDIUM FIDELITY (70-89): Some drift occurring.")
            print("  → Consider adding judge validation in UI")
            print("  → May need prompt tuning")
            print("  → Review low-scoring dimensions for patterns")
        else:
            print("✗ LOW FIDELITY (<70): Significant identity loss.")
            print("  → Fundamental problem with current approach")
            print("  → Need explicit identity linking (proto-recipe concept)")
            print("  → Consider richer context passing between pitch and recipe")

        print(f"\nLowest scoring dimension: ", end="")
        if avg_ingredient <= min(avg_effort, avg_experience, avg_character):
            print(
                "Ingredient Alignment - recipes using different ingredients than expected"
            )
        elif avg_effort <= min(avg_ingredient, avg_experience, avg_character):
            print("Effort Alignment - time/complexity not matching promises")
        elif avg_experience <= min(avg_ingredient, avg_effort, avg_character):
            print("Experience Alignment - not delivering on emotional/sensory promises")
        else:
            print("Character Preservation - losing voice and personality of original")

    if failed_tests:
        print(f"\n\nFailed tests:")
        for result in failed_tests:
            print(f"  ✗ {result['recipe_name']}: {result['error']}")

    print(f"\n\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save detailed results to JSON file
    output_dir = Path(__file__).parent.parent.parent / ".scratch"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_file = output_dir / f"fidelity-test-detailed-{timestamp}.json"

    # Convert results to serializable format (they already are serializable)
    serializable_results = results

    with open(json_file, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "summary": {
                    "total_tests": len(results),
                    "successful": len(successful_tests),
                    "failed": len(failed_tests),
                    "averages": {
                        "overall": avg_overall if successful_tests else 0,
                        "ingredient_alignment": avg_ingredient
                        if successful_tests
                        else 0,
                        "effort_alignment": avg_effort if successful_tests else 0,
                        "experience_alignment": avg_experience
                        if successful_tests
                        else 0,
                        "character_preservation": avg_character
                        if successful_tests
                        else 0,
                    }
                    if successful_tests
                    else None,
                },
                "results": serializable_results,
            },
            f,
            indent=2,
        )

    print(f"\nDetailed results saved to: {json_file}")

    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
