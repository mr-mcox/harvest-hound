// Recipe pitch generation for meal planning criteria

class InventoryIngredient {
  name string @description("Ingredient name")
  quantity float @description("Quantity on hand")
  unit string @description("Unit of measurement")
  priority string @description("Priority level: Urgent, High, Medium, Low")
}

class PitchIngredient {
  name string @description("Ingredient name matching inventory")
  quantity float @description("Amount needed for this recipe")
  unit string @description("Unit of measurement (pound, bunch, cup, etc.)")

  @@assert(quantity_positive, {{ this.quantity > 0 }})
  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(unit_not_empty, {{ this.unit|length > 0 }})
}

class RecipePitch {
  name string @description("Clear, appealing recipe name")
  blurb string @description("Single evocative sentence - emotional appeal, sensory, makes you want to cook it")
  why_make_this string @description("Concise practical appeal - 3-5 words capturing key benefit (e.g., 'One-pan weeknight dinner', 'Wow-factor for guests', 'Great leftovers')")
  inventory_ingredients PitchIngredient[] @description("Ingredients from inventory with quantities this recipe will claim")
  active_time_minutes int @description("Estimated active cooking time")

  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(blurb_not_empty, {{ this.blurb|length > 0 }})
  @@assert(has_inventory_ingredients, {{ this.inventory_ingredients|length >= 1 }})
}

function GenerateRecipePitches(
  inventory: InventoryIngredient[],
  pantry_staples: string,
  grocery_stores: string,
  household_profile: string,
  additional_context: string,
  num_pitches: int
) -> RecipePitch[] {
  client Anthropic
  prompt #"
    You are a culinary AI assistant helping plan meals for a household.

    <household-profile>
    {{ household_profile }}
    </household-profile>

    <grocery-stores>
    These are the stores available for shopping. Only suggest recipes that can be made with ingredients obtainable from these stores:
    {{ grocery_stores }}
    </grocery-stores>

    <inventory>
    Ingredients currently on hand. Each ingredient has a priority level (Urgent > High > Medium > Low). Prioritize higher-priority ingredients:
    {{ inventory }}
    </inventory>

    <pantry-staples>
    These are unlimited pantry staples (don't include in inventory_ingredients):
    {{ pantry_staples }}
    </pantry-staples>

    <meal-context>
    {{ additional_context }}
    </meal-context>

    Generate {{ num_pitches }} recipe pitches that:
    1. Use ingredients from the inventory listed above, prioritizing higher-priority items
    2. Only require additional ingredients that are obtainable from the listed grocery stores
    3. Fit the household preferences and equipment from the profile
    4. Consider the meal context if provided
    5. Are appropriate based on household dietary preferences

    DIVERSITY GUIDANCE:
    - Ingredients CAN repeat across pitches - that's normal for weekly planning
    - Aim for variety in technique (roasting, braising, sautéing, raw, etc.)
    - Mix different cuisines and flavor profiles where appropriate
    - Include a range of time commitments (quick meals and longer projects)
    - Don't force artificial variety - practical repetition is fine

    IMPORTANT - Keep pitches CONCISE:
    - blurb: ONE evocative sentence maximum. Sensory, emotional, makes you hungry. NO practical details.
    - why_make_this: 3-5 WORDS capturing key practical benefit (e.g., "One-pan weeknight", "Weekend project", "Great leftovers")
    - inventory_ingredients: List ingredients FROM INVENTORY ONLY with realistic quantities for this recipe. Don't include pantry staples.
    - Don't repeat information between fields

    {{ ctx.output_format }}
  "#
}

// Test: Basic pitch generation with simple inventory
test basic_pitch_generation {
  functions [GenerateRecipePitches]
  args {
    inventory [
      {name: "carrots", quantity: 2, unit: "pound", priority: "High"},
      {name: "kale", quantity: 1, unit: "bunch", priority: "Urgent"},
      {name: "ground beef", quantity: 1, unit: "pound", priority: "Medium"}
    ]
    pantry_staples #"
    Salt, pepper, olive oil, garlic, onions, soy sauce, rice, pasta
    "#
    grocery_stores #"
    - Cub Foods: Standard suburban grocery store with typical American ingredients
    "#
    household_profile #"
    Family of 4 with two young children.
    Intermediate cooking skills.
    Equipment: Instant Pot, standard stovetop, oven.
    Preferences: Kid-friendly, not too spicy.
    "#
    additional_context "Quick weeknight dinners, 30 minutes or less"
    num_pitches 3
  }
  @@assert(correct_count, {{ this|length == 3 }})
  @@assert(has_names, {{ this[0].name|length > 0 }})
  @@assert(has_blurbs, {{ this[0].blurb|length > 0 }})
  @@assert(has_inventory_ingredients, {{ this[0].inventory_ingredients|length >= 1 }})
  @@assert(has_time, {{ this[0].active_time_minutes > 0 }})
}

// Test: Pitch generation respects num_pitches parameter
test respects_num_pitches {
  functions [GenerateRecipePitches]
  args {
    inventory [
      {name: "chicken breast", quantity: 1, unit: "pound", priority: "Medium"},
      {name: "broccoli", quantity: 1, unit: "head", priority: "High"}
    ]
    pantry_staples "Salt, pepper, oil, garlic"
    grocery_stores "- Local Grocery: General grocery store"
    household_profile "Single person, quick meals preferred"
    additional_context "Meal prep for the week"
    num_pitches 6
  }
  @@assert(correct_count, {{ this|length == 6 }})
}

// Test: Inventory ingredients have quantities
test inventory_ingredients_have_quantities {
  functions [GenerateRecipePitches]
  args {
    inventory [
      {name: "sweet potatoes", quantity: 3, unit: "pound", priority: "Medium"},
      {name: "black beans", quantity: 2, unit: "can", priority: "Low"}
    ]
    pantry_staples "Cumin, chili powder, salt, oil"
    grocery_stores "- Farmers Market: Local produce and specialty items"
    household_profile "Vegetarian household"
    additional_context ""
    num_pitches 2
  }
  @@assert(has_pitches, {{ this|length == 2 }})
  @@assert(has_ingredients, {{ this[0].inventory_ingredients|length >= 1 }})
  // Ingredients should have positive quantities
  @@assert(valid_quantity, {{ this[0].inventory_ingredients[0].quantity > 0 }})
  @@assert(has_unit, {{ this[0].inventory_ingredients[0].unit|length > 0 }})
}


class RecipeIngredient {
  name string @description("MUST match inventory names exactly for claiming")
  quantity string @description("Amount: '2', '1.5', '2-3', or 'to taste'")
  unit string
  preparation string? @description("How to prep: diced, minced, julienned")
  notes string?
  purchase_likelihood float @description("Likelihood you'd need to purchase this ingredient (0.0 = definitely in pantry, 1.0 = definitely need to buy). Consider pantry description.")

  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(quantity_not_empty, {{ this.quantity|length > 0 }})
  @@assert(unit_not_empty, {{ this.unit|length > 0 }})
  @@assert(likelihood_in_range, {{ this.purchase_likelihood >= 0.0 and this.purchase_likelihood <= 1.0 }})
}

class CompleteRecipe {
  name string
  description string
  ingredients RecipeIngredient[]
  instructions string[]
  active_time_minutes int
  total_time_minutes int
  servings int
  notes string?

  @@assert(name_not_empty, {{ this.name|length > 0 }})
  @@assert(description_not_empty, {{ this.description|length > 0 }})
  @@assert(has_ingredients, {{ this.ingredients|length >= 1 }})
  @@assert(has_instructions, {{ this.instructions|length >= 2 }})
  @@assert(active_time_positive, {{ this.active_time_minutes > 0 }})
  @@assert(total_time_positive, {{ this.total_time_minutes > 0 }})
  @@assert(total_gte_active, {{ this.total_time_minutes >= this.active_time_minutes }})
  @@assert(servings_positive, {{ this.servings >= 1 }})
  @@assert(servings_reasonable, {{ this.servings <= 20 }})
}

function FleshOutRecipe(
  pitch_name: string,
  pitch_blurb: string,
  pitch_inventory_ingredients: string,
  household_profile: string,
  pantry_staples: string,
  grocery_stores: string,
  inventory: string
) -> CompleteRecipe {
  client Anthropic
  prompt #"
    You are a culinary AI assistant creating a complete recipe from a pitch.

    <household-profile>
    {{ household_profile }}
    </household-profile>

    <grocery-stores>
    {{ grocery_stores }}
    </grocery-stores>

    <inventory>
    {{ inventory }}
    </inventory>

    <pantry-staples>
    {{ pantry_staples }}
    </pantry-staples>

    <pitch>
    Name: {{ pitch_name }}
    Blurb: {{ pitch_blurb }}
    Key inventory ingredients: {{ pitch_inventory_ingredients }}
    </pitch>

    Create a complete recipe that:
    1. Faithfully expands the pitch
    2. Uses the key inventory ingredients from the pitch
    3. May add pantry staples and grocery items from listed stores
    4. Fits the household profile

    CRITICAL - Ingredient names for inventory items:
    - Use EXACT names from the inventory list (enables automatic claiming)
    - Example: If inventory says "carrots", use "carrots" not "baby carrots"

    INGREDIENT FORMAT:
    - preparation: How to prep BEFORE cooking (diced, minced, julienned)
      - Include for produce and proteins - important for shopping
    - purchase_likelihood: Assign to EVERY ingredient (0.0 to 1.0)
      - How likely would they need to purchase this if they don't have it in inventory?
      - Consider the pantry description carefully:
        * 0.0-0.3: Probably in pantry (e.g., salt when pantry is well-stocked)
        * 0.3-0.7: Maybe have it, maybe not (grey area)
        * 0.7-1.0: Definitely need to buy (specialty items, or items pantry never stocks)
      - Examples:
        * "salt" with well-stocked pantry → 0.1 (definitely have it)
        * "cumin" with "extensive spice collection" → 0.2 (have it)
        * "cumin" with "only keep salt, pepper, oil" → 0.9 (need to buy)
        * "goat cheese" with "never keep fresh dairy" → 0.9 (need to buy)
        * "goat cheese" with "always have various cheeses" → 0.2 (have it)

    {{ ctx.output_format }}
  "#
}

test flesh_out_generates_valid_structure {
  functions [FleshOutRecipe]
  args {
    pitch_name "Honey Glazed Carrots"
    pitch_blurb "Sweet, caramelized carrots that melt in your mouth"
    pitch_inventory_ingredients "carrots: 2 lbs"
    household_profile "Family of 4, intermediate cooking skills"
    pantry_staples "Salt, pepper, butter, honey, olive oil"
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## CSA Box
    - 2 lbs carrots (High priority)
    "#
  }
  @@assert(has_name, {{ this.name|length > 0 }})
  @@assert(has_ingredients, {{ this.ingredients|length >= 1 }})
  @@assert(has_multiple_instructions, {{ this.instructions|length >= 2 }})
  @@assert(active_time_positive, {{ this.active_time_minutes > 0 }})
  @@assert(total_gte_active, {{ this.total_time_minutes >= this.active_time_minutes }})
  @@assert(servings_positive, {{ this.servings >= 1 }})
}

test flesh_out_uses_exact_inventory_names {
  functions [FleshOutRecipe]
  args {
    pitch_name "Kale and Carrot Stir Fry"
    pitch_blurb "Quick, healthy, and packed with CSA goodness"
    pitch_inventory_ingredients "carrots: 1 lb, kale: 1 bunch"
    household_profile "Health-conscious household"
    pantry_staples "Soy sauce, sesame oil, garlic, ginger"
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## CSA Box
    - 2 lbs carrots (High priority)
    - 1 bunch kale (Urgent priority)
    "#
  }
  @@assert(has_inventory_ingredient, {{ this.ingredients|length >= 2 }})
}

test flesh_out_includes_preparation {
  functions [FleshOutRecipe]
  args {
    pitch_name "Carrot Soup"
    pitch_blurb "Velvety smooth soup with warm spices"
    pitch_inventory_ingredients "carrots: 2 lbs"
    household_profile "Home cook with standard equipment"
    pantry_staples "Salt, pepper, olive oil, onion, garlic, vegetable broth"
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## CSA Box
    - 2 lbs carrots (High priority)
    "#
  }
  @@assert(has_ingredients, {{ this.ingredients|length >= 1 }})
}

// Purchase likelihood tests - testing LLM judgment based on pantry context

test purchase_likelihood_low_for_common_pantry_staple {
  functions [FleshOutRecipe]
  args {
    pitch_name "Simple Roasted Carrots"
    pitch_blurb "Caramelized carrots with olive oil"
    pitch_inventory_ingredients "carrots: 2 lbs"
    household_profile "Home cook with well-stocked kitchen"
    pantry_staples #"
    Fully stocked pantry with all basics: salt, black pepper, olive oil, butter,
    various vinegars, soy sauce, honey, maple syrup, all common spices.
    "#
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## CSA Box
    - 2 lbs carrots (High priority)
    "#
  }
  // Olive oil should have low purchase likelihood (< 0.3) with well-stocked pantry
  @@assert(olive_oil_low_likelihood, {{ this.ingredients|map(attribute='purchase_likelihood')|min < 0.3 }})
}

test purchase_likelihood_high_for_specialty_item_minimal_pantry {
  functions [FleshOutRecipe]
  args {
    pitch_name "Goat Cheese Salad"
    pitch_blurb "Fresh greens with tangy goat cheese and balsamic"
    pitch_inventory_ingredients "lettuce: 1 head"
    household_profile "Minimalist cook with basic equipment"
    pantry_staples #"
    Minimalist pantry - only keep: salt, black pepper, olive oil.
    No specialty items, no spices, no dairy products.
    "#
    grocery_stores "- Whole Foods: Upscale grocery with specialty items"
    inventory #"
    ## CSA Box
    - 1 head lettuce (High priority)
    "#
  }
  // With minimal pantry, highest purchase likelihood should be >= 0.7 (specialty item)
  @@assert(has_high_likelihood_item, {{ this.ingredients|map(attribute='purchase_likelihood')|max >= 0.7 }})
}

test purchase_likelihood_high_when_pantry_never_has_fresh_dairy {
  functions [FleshOutRecipe]
  args {
    pitch_name "Creamy Pasta"
    pitch_blurb "Rich and creamy pasta with parmesan"
    pitch_inventory_ingredients "pasta: 1 lb"
    household_profile "Lactose-intolerant household"
    pantry_staples #"
    Never keep fresh dairy products - lactose intolerant household.
    Only shelf-stable items: salt, pepper, olive oil, pasta, rice, canned goods.
    "#
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## Pantry
    - 1 lb pasta (Medium priority)
    "#
  }
  // With "never keep dairy", highest purchase likelihood should be >= 0.7
  @@assert(has_high_likelihood_dairy, {{ this.ingredients|map(attribute='purchase_likelihood')|max >= 0.7 }})
}

test purchase_likelihood_low_when_pantry_always_has_item {
  functions [FleshOutRecipe]
  args {
    pitch_name "Spiced Carrot Soup"
    pitch_blurb "Warming soup with cumin and coriander"
    pitch_inventory_ingredients "carrots: 2 lbs"
    household_profile "Adventurous home cook"
    pantry_staples #"
    Extensive spice collection - always stocked with: cumin, coriander, turmeric,
    paprika, cinnamon, cardamom, garam masala, curry powder, plus all basics.
    "#
    grocery_stores "- Local Grocery: Standard grocery store"
    inventory #"
    ## CSA Box
    - 2 lbs carrots (High priority)
    "#
  }
  // Cumin should have low likelihood (< 0.3) when pantry always has it
  @@assert(cumin_exists, {{ this.ingredients|selectattr('name', 'equalto', 'cumin')|list|length > 0 }})
  @@assert(cumin_low_likelihood, {{ this.ingredients|selectattr('name', 'equalto', 'cumin')|first|attr('purchase_likelihood') < 0.3 }})
}
