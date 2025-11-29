class RecipeIngredient {
  name string
  quantity float
  unit string

  @@assert(quantity_positive, {{ this.quantity > 0 }})
  @@assert(name_not_empty, {{ this.name|length > 0 }})
}

class Recipe {
  name string @description("Clear, appealing recipe name")
  ingredients RecipeIngredient[] @description("Complete ingredient list with measurements")
  instructions string @description("Step-by-step cooking instructions")
  active_time_minutes int @description("Active cooking time (prep + hands-on)")
  passive_time_minutes int? @description("Passive time (baking, simmering, etc.)")
  servings int @description("Number of servings this recipe makes")
  notes string? @description("Tips, variations, or prep-ahead suggestions")

  @@assert(name_length, {{ this.name|length > 0 }})
  @@assert(has_ingredients, {{ this.ingredients|length > 0 }})
  @@assert(has_instructions, {{ this.instructions|length > 0 }})
}

function GenerateSingleRecipe(
  available_inventory: string,
  additional_context: string,
  recipes_already_generated: string
) -> Recipe {
  client "openai/gpt-4o-mini"
  prompt #"
    You are a specialized culinary AI assistant for a family of four with two young children who prefer non-spicy foods.

    <household-context>
    - Intermediate cooking skills (comfortable with sautéing, braising, making roux)
    - Well-stocked pantry focusing on Italian and Indian cuisines
    - Regular CSA deliveries (prioritize these fresh ingredients)
    - Freezer with various meats
    - Children enjoy pasta, rice, slight preference for Mexican flavors

    Equipment available:
    - Instant Pot, sous vide, food processor, blender
    - Pasta maker, tortilla press, pizza stone, crock pot

    Cooking preferences:
    - PRIORITIZE low active cooking time over total time
      (20 min prep + 3 hours passive > 45 min active)
    - Balance one-pot meals with "protein + vegetable side" combinations
    - Emphasize creative and flavorful vegetable preparations
    - Design for intentional leftovers for lunches
    - Accommodate seasonal produce (winter staples: cabbage, sweet potatoes, etc.)
    - Kid-friendly but flavorful
    </household-context>

    <available-inventory>
    {{ available_inventory }}
    </available-inventory>

    <user-context>
    {{ additional_context }}
    </user-context>

    <recipes-already-generated>
    {{ recipes_already_generated }}
    </recipes-already-generated>

    Generate ONE recipe that:
    1. Uses ingredients from the available inventory (especially fresh CSA items)
    2. Fits the household preferences and equipment
    3. Considers the user's additional context if provided
    4. Is DIFFERENT from any recipes already generated
    5. Minimizes active cooking time while maximizing flavor
    6. Is appropriate for young children (not spicy)

    DO NOT include leftover application suggestions.

    {{ ctx.output_format }}
  "#
}
