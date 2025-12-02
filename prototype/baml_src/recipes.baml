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

// Generate a pitch from an existing recipe (reverse direction)
function GeneratePitchFromRecipe(
  recipe_name: string,
  recipe_ingredients: string,
  recipe_instructions: string,
  recipe_description: string
) -> RecipePitch {
  client Anthropic
  prompt #"
    You are creating a compelling pitch for an existing recipe.

    Your goal is to capture the ESSENCE and CHARACTER of this recipe in a browsable pitch format.

    <recipe>
    Name: {{ recipe_name }}

    {% if recipe_description %}
    Description: {{ recipe_description }}
    {% endif %}

    Ingredients:
    {{ recipe_ingredients }}

    Instructions:
    {{ recipe_instructions }}
    </recipe>

    Generate a RecipePitch that:
    1. Preserves the VOICE and CHARACTER of the original recipe
       - If the recipe has a personal story, reflect that in the blurb
       - If it mentions cultural context, honor that
       - If it has dramatic language ("bravery", "patience"), keep that energy

    2. Accurately represents the EFFORT and TECHNIQUE
       - If it's a slow braise, the pitch should suggest that
       - If it's a quick weeknight meal, convey speed
       - If it has unusual techniques (charring, flipping), hint at that

    3. Highlights the CORE INGREDIENTS that define the dish
       - Focus on what makes this recipe distinctive
       - List 3-5 key ingredients (not every ingredient)

    4. Creates ACCURATE EXPECTATIONS
       - The blurb should set up what the fleshed-out recipe will deliver
       - Don't promise something the recipe doesn't provide
       - If it's complex, don't make it sound simple

    IMPORTANT - Pitch Structure:
    - name: Use the exact recipe name
    - blurb: ONE evocative sentence capturing the recipe's character/appeal
    - why_make_this: 3-5 words capturing practical benefit
    - key_ingredients: 3-5 main ingredients (semantic names, not quantities)
    - explicit_ingredients: For this test, mark all ingredients as from "Test Store"
    - active_time_minutes: Estimate based on instructions

    {{ ctx.output_format }}
  "#
}

// Fidelity scoring across multiple dimensions
class FidelityScore {
  ingredient_alignment int @description("0-100: Do core ingredients match between original and generated?")
  ingredient_reasoning string @description("Explanation of ingredient alignment score")

  effort_alignment int @description("0-100: Is time/complexity/technique as expected?")
  effort_reasoning string @description("Explanation of effort alignment score")

  experience_alignment int @description("0-100: Does generated recipe deliver on pitch/original's promise?")
  experience_reasoning string @description("Explanation of experience alignment score")

  character_preservation int @description("0-100: Is the voice, style, and personality preserved?")
  character_reasoning string @description("Explanation of character preservation score")

  overall_score int @description("0-100: Overall fidelity (weighted average)")
  overall_assessment string @description("Summary assessment of fidelity")
}

// Judge fidelity: Does the round-trip maintain recipe identity?
function JudgeFidelity(
  original_recipe_name: string,
  original_recipe_description: string,
  original_ingredients: string,
  original_instructions: string,
  pitch_name: string,
  pitch_blurb: string,
  pitch_why_make_this: string,
  generated_recipe_name: string,
  generated_ingredients: string,
  generated_instructions: string
) -> FidelityScore {
  client Anthropic
  prompt #"
    You are evaluating whether a recipe survived a round-trip transformation:
    Original Recipe → Pitch → Generated Recipe

    Your job is to assess FIDELITY across multiple dimensions.

    <original-recipe>
    Name: {{ original_recipe_name }}
    {% if original_recipe_description %}
    Description: {{ original_recipe_description }}
    {% endif %}

    Ingredients:
    {{ original_ingredients }}

    Instructions:
    {{ original_instructions }}
    </original-recipe>

    <pitch>
    Name: {{ pitch_name }}
    Blurb: {{ pitch_blurb }}
    Why Make This: {{ pitch_why_make_this }}
    </pitch>

    <generated-recipe>
    Name: {{ generated_recipe_name }}

    Ingredients:
    {{ generated_ingredients }}

    Instructions:
    {{ generated_instructions }}
    </generated-recipe>

    Evaluate fidelity across these dimensions:

    1. INGREDIENT ALIGNMENT (0-100)
       - Do the core/defining ingredients match?
       - Minor substitutions are OK (e.g., "yellow onion" vs "white onion")
       - Major omissions or additions should lower score
       - Focus on IDENTITY-DEFINING ingredients, not every detail

    2. EFFORT ALIGNMENT (0-100)
       - Is the time commitment similar?
       - Is the technique complexity similar?
       - Would someone selecting the pitch get what they expected?
       - 10-min difference in time is OK; 30+ min is not

    3. EXPERIENCE ALIGNMENT (0-100)
       - Does the generated recipe deliver on the pitch's promise?
       - If pitch said "comfort food", is generated recipe comforting?
       - If pitch suggested "quick weeknight", is it actually quick?
       - Does it fulfill the emotional/sensory expectations?

    4. CHARACTER PRESERVATION (0-100)
       - If original had distinctive voice, is it preserved?
       - If original had cultural context, is it honored?
       - If original had dramatic language ("bravery", "patience"), is that energy maintained?
       - Would someone who loved the original recognize this version?

    5. OVERALL SCORE (0-100)
       Calculate weighted average:
       - Ingredient alignment: 30%
       - Effort alignment: 25%
       - Experience alignment: 25%
       - Character preservation: 20%

    Be honest and specific in your reasoning. This is a research evaluation.

    {{ ctx.output_format }}
  "#
}
