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

// Lightweight recipe pitch for browsing
class RecipePitch {
  name string @description("Clear, appealing recipe name")
  blurb string @description("Single evocative sentence - emotional appeal, sensory, makes you want to cook it")
  why_make_this string @description("Concise practical appeal - 3-5 words capturing key benefit (e.g., 'One-pan weeknight dinner', 'Wow-factor for guests', 'Great leftovers')")
  key_ingredients string[] @description("3-5 main ingredients that will be used")
  active_time_minutes int @description("Estimated active cooking time")

  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(blurb_not_empty, {{ this.blurb|length > 0 }})
  @@assert(has_key_ingredients, {{ this.key_ingredients|length >= 3 }})
}

function GenerateRecipePitches(
  available_inventory: string,
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

    <available-inventory>
    {{ available_inventory }}
    </available-inventory>

    <user-context>
    {{ additional_context }}
    </user-context>

    Generate {{ num_pitches }} DIVERSE recipe pitches that:
    1. Use ingredients from the available inventory listed above
    2. Prioritize fresh CSA items that will spoil soon
    3. Fit the household preferences and equipment
    4. Consider the user's additional context if provided
    5. Are MAXIMALLY DIVERSE from each other:
       - Different techniques (roasting, braising, raw, pickled, grilled, etc.)
       - Different flavor profiles (bright & acidic, rich & savory, sweet & tangy)
       - Different cuisines and styles
       - DIFFERENT TIME COMMITMENTS (mix quick 15-min meals with leisurely 60-min weekend projects)
       - Different formats (one-pot, protein+sides, bowls, tacos, etc.)
    6. Are appropriate for young children (not spicy)

    IMPORTANT - Keep pitches CONCISE:
    - blurb: ONE evocative sentence maximum. Sensory, emotional, makes you hungry. NO practical details.
    - why_make_this: 3-5 WORDS capturing key practical benefit (e.g., "One-pan weeknight", "Weekend project", "Great leftovers")
    - Don't repeat information between fields

    Be creative and diverse - if you suggest roasted radishes, also suggest quick-pickled radishes, radish tacos, radish greens pesto, etc.

    {{ ctx.output_format }}
  "#
}

function GenerateSingleRecipe(
  available_inventory: string,
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
    1. Uses ingredients from the available inventory listed above
    2. Prioritizes fresh CSA items that will spoil soon
    3. Fits the household preferences and equipment
    4. Considers the user's additional context if provided
    5. Is DIFFERENT from any recipes already generated
    6. Minimizes active cooking time while maximizing flavor
    7. Is appropriate for young children (not spicy)

    {{ ctx.output_format }}
  "#
}
