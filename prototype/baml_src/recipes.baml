class RecipeIngredient {
  name string
  quantity float
  unit string
  store string @description("Which store this ingredient comes from (exact store name)")

  @@assert(quantity_positive, {{ this.quantity > 0 }})
  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(store_not_empty, {{ this.store|length > 0 }})
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

// Lightweight recipe pitch for browsing
class RecipePitch {
  name string @description("Clear, appealing recipe name")
  blurb string @description("Single evocative sentence - emotional appeal, sensory, makes you want to cook it")
  why_make_this string @description("Concise practical appeal - 3-5 words capturing key benefit (e.g., 'One-pan weeknight dinner', 'Wow-factor for guests', 'Great leftovers')")
  key_ingredients string[] @description("3-5 main ingredients that will be used")
  explicit_ingredients RecipeIngredient[] @description("Structured list of explicit store ingredients with quantities that this recipe will claim")
  active_time_minutes int @description("Estimated active cooking time")

  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(blurb_not_empty, {{ this.blurb|length > 0 }})
  @@assert(has_key_ingredients, {{ this.key_ingredients|length >= 3 }})
}

function GenerateRecipePitches(
  explicit_stores: string,
  definition_stores: string,
  additional_context: string,
  num_pitches: int
) -> RecipePitch[] {
  client Anthropic
  prompt #"
    You are a specialized culinary AI assistant for a family of four with two young children who prefer non-spicy foods.

    <household-context>
    - Intermediate cooking skills (comfortable with sautéing, braising, making roux)
    - Freezer with various meats
    - Children enjoy pasta, rice, slight preference for Mexican flavors

    Equipment available:
    - Instant Pot, sous vide, food processor, blender
    - Pasta maker, tortilla press, pizza stone, crock pot

    Cooking preferences:
    - Balance one-pot meals with "protein + vegetable side" combinations
    - Emphasize creative and flavorful vegetable preparations
    - Design for intentional leftovers for lunches
    - Accommodate seasonal produce (winter staples: cabbage, sweet potatoes, etc.)
    - Kid-friendly but flavorful
    </household-context>

    <explicit-stores>
    These are ingredients with specific quantities that need to be claimed (use them explicitly in your pitches):
    {{ explicit_stores }}
    </explicit-stores>

    <definition-stores>
    These are unlimited pantry staples (don't list in explicit_ingredients):
    {{ definition_stores }}
    </definition-stores>

    <user-context>
    {{ additional_context }}
    </user-context>

    Generate {{ num_pitches }} DIVERSE recipe pitches that:
    1. PRIORITIZE fresh CSA items that will spoil soon - generate MULTIPLE creative options for the same fresh ingredient
    2. Use ingredients from the explicit stores listed above
    3. Fit the household preferences and equipment
    4. Consider the user's additional context if provided
    5. Are diverse in TECHNIQUE, not ingredient choice:
       - If you have radishes, suggest: roasted radishes, quick-pickled radishes, radish tacos, radish greens pesto, radish salad, etc.
       - Different techniques (roasting, braising, raw, pickled, grilled, sautéed, fermented)
       - Different flavor profiles (bright & acidic, rich & savory, sweet & tangy, funky & fermented)
       - Different cuisines and styles (Mexican, Italian, Asian, comfort food)
       - DIFFERENT TIME COMMITMENTS (mix quick 15-min meals with leisurely 60-min weekend projects)
       - Different formats (one-pot, protein+sides, bowls, tacos, salads, sides)
    6. Are appropriate for young children (not spicy)

    CRITICAL: Don't artificially limit yourself to one pitch per ingredient. If radishes are the main CSA item, 5-7 radish recipes with different techniques is BETTER than forcing diversity across ingredients. Fresh items spoil - give multiple options!

    IMPORTANT - Keep pitches CONCISE:
    - blurb: ONE evocative sentence maximum. Sensory, emotional, makes you hungry. NO practical details.
    - why_make_this: 3-5 WORDS capturing key practical benefit (e.g., "One-pan weeknight", "Weekend project", "Great leftovers")
    - explicit_ingredients: List ONLY ingredients from explicit stores with quantities (not pantry staples)
    - Don't repeat information between fields

    {{ ctx.output_format }}
  "#
}

function GenerateSingleRecipe(
  explicit_stores: string,
  definition_stores: string,
  additional_context: string,
  recipes_already_generated: string
) -> Recipe {
  client Anthropic
  prompt #"
    You are a specialized culinary AI assistant for a family of four with two young children who prefer non-spicy foods.

    <household-context>
    - Intermediate cooking skills (comfortable with sautéing, braising, making roux)
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

    <explicit-stores>
    These are ingredients with specific quantities available:
    {{ explicit_stores }}
    </explicit-stores>

    <definition-stores>
    These are unlimited pantry staples:
    {{ definition_stores }}
    </definition-stores>

    <user-context>
    {{ additional_context }}
    </user-context>

    <recipes-already-generated>
    {{ recipes_already_generated }}
    </recipes-already-generated>

    Generate ONE recipe that:
    1. Uses ingredients from the explicit stores listed above
    2. Prioritizes fresh CSA items that will spoil soon
    3. Fits the household preferences and equipment
    4. Considers the user's additional context if provided
    5. Is DIFFERENT from any recipes already generated
    6. Minimizes active cooking time while maximizing flavor
    7. Is appropriate for young children (not spicy)

    CRITICAL - Store Assignment for EVERY Ingredient:
    You MUST assign a store to EVERY ingredient in the recipe. Use these rules:
    - If ingredient is in explicit stores → use that exact store name
    - If ingredient is in definition stores → use that exact store name
    - If ingredient is NOT in any listed store → use "Cub foods" (the grocery store)

    Example: If recipe needs goat cheese and it's not listed in any store, set store="Cub foods"
    This ensures we can generate complete shopping lists.

    {{ ctx.output_format }}
  "#
}
