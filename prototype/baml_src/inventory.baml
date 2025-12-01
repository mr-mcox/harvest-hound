class Ingredient {
    name string
    quantity float
    unit string
    priority string  // low, medium, high, urgent

    @@assert(positive_quantity, {{ this.quantity > 0 }})
    @@assert(name_not_empty, {{ this.name|length > 0 }})
    @@assert(unit_not_empty, {{ this.unit|length > 0 }})
}

class InventoryParsingResult {
    ingredients Ingredient[]
    parsing_notes string?
}

function ExtractIngredients(text: string, store_context: string?) -> InventoryParsingResult {
    client "openai/gpt-4o-mini"
    prompt #"
        This text contains a list of ingredients for a grocery/food inventory system.
        <text>
        {{ text }}
        </text>

        {% if store_context %}
        <store_context>
        {{ store_context }}

        Use this context to inform your parsing assumptions, especially for portion sizes and units.
        </store_context>
        {% endif %}

        Extract the ingredients from the text that are valid food items. Skip any items that are clearly not food ingredients.

        For the ingredients array: Include only items that you can confidently parse as valid food ingredients with reasonable quantities.

        For the parsing_notes field: If you encountered any problematic items while parsing, provide a brief natural language explanation. Examples of issues to note:
        - Items that don't appear to be food ingredients (e.g., "car tires", "homework", "Volvos")
        - Items with unclear or impossible quantities (e.g., "3 gazillion eggs", "negative 5 apples")
        - Items too vague to parse meaningfully (e.g., "some stuff", "food")
        - Leave this field null if all items were parsed successfully

        Normalize valid ingredients with these guidelines:
        <guidelines>
        <ingredient>
        - Are singular and lowercase
        - Use common ingredient names (e.g., "carrot" not "baby carrot")
        </ingredient>
        <unit>
        - Use full names (pound, ounce, cup, tablespoon, teaspoon, bunch, head, roast, chop, etc.)
        - Are singular and lowercase
        - For meats: Use item-based units when appropriate (roast, chop, steak, etc.) rather than weights
        - When you see "xN" notation (e.g., "x3", "x2"), this indicates COUNT of items
          * "Butt Roast x3" = 3 roasts (each roast is a separate item)
          * "Pork chops x4" = 4 chops (each chop is a separate item)
          * Use the item unit (roast, chop) and the count as quantity
        - If unspecified, use the most reasonable unit for that ingredient
        </unit>
        <quantity>
        - If unspecified, use a reasonable quantity one would purchase
        - Always use numbers, never words (2 not "two")
        - When parsing "xN" notation, the number N is the quantity and the item type is the unit
        </quantity>
        <priority>
        - Suggest a priority level for each ingredient: "low", "medium", "high", or "urgent"
        - Priority guidelines:
          * "urgent" - Fresh items that spoil quickly (leafy greens, herbs, berries, cream, soft cheeses)
          * "high" - Items that should be used relatively soon (other fresh vegetables, fresh meat in fridge)
          * "medium" - Default for most items (frozen meat, root vegetables, pantry staples with decent shelf life)
          * "low" - Long shelf life items (dried goods, canned items, frozen vegetables, freezer meat)
        - Use your judgment based on typical shelf life and perishability
        </priority>
        </guidelines>

        {{ ctx.output_format }}
    "#
}

test carrots_single_ingredient {
    functions [ExtractIngredients]
    args {
        text #"
        - 2 lbs carrots
        "#
        store_context null
    }
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[0].quantity == 2}})
    @@assert({{this.ingredients[0].unit == "pound"}})
}

test kale_with_bunch {
    functions [ExtractIngredients]
    args {
        text "1 bunch kale"
        store_context null
    }
    @@assert({{this.ingredients[0].name == "kale"}})
    @@assert({{this.ingredients[0].quantity == 1}})
    @@assert({{this.ingredients[0].unit == "bunch"}})
}

test multi_line_ingredients {
    functions [ExtractIngredients]
    args {
        text #"
        2 lbs carrots
        1 bunch kale
        "#
        store_context null
    }
    @@assert({{this.ingredients|length == 2}})
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[1].name == "kale"}})
}

test carrots_rice {
    functions [ExtractIngredients]
    args {
        text #"
        - 2 lbs carrots\n- 1/2 cup rice
        "#
        store_context null
    }
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[0].quantity == 2}})
    @@assert({{this.ingredients[0].unit == "pound"}})
    @@assert({{this.ingredients[1].name == "rice"}})
    @@assert({{this.ingredients[1].quantity == 0.5}})
    @@assert({{this.ingredients[1].unit == "cup"}})
}

test csv_format {
    functions [ExtractIngredients]
    args {
        text "carrots, 2, lbs"
        store_context null
    }
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[0].quantity == 2}})
    @@assert({{this.ingredients[0].unit == "pound"}})
}

test empty_input {
    functions [ExtractIngredients]
    args {
        text ""
        store_context null
    }
    @@assert({{this.ingredients|length == 0}})
}

test with_problematic_items {
    functions [ExtractIngredients]
    args {
        text #"
        2 lbs carrots
        1 Volvo car
        3 gazillion eggs
        1 bunch kale
        "#
        store_context null
    }
    @@assert({{this.ingredients|length == 2}})
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[1].name == "kale"}})
    @@assert({{this.parsing_notes != null}})
}

test meat_with_x_notation {
    functions [ExtractIngredients]
    args {
        text #"
        - Pork
            - Butt Roast x3
            - Loin chops x4
            - Ground
        "#
        store_context "Freezer meat storage. Portions are typically 1 lb unless otherwise specified."
    }
    @@assert({{this.ingredients|length == 3}})
    @@assert({{this.ingredients[0].quantity == 3}})
    @@assert({{this.ingredients[0].unit == "roast"}})
    @@assert({{this.ingredients[1].quantity == 4}})
    @@assert({{this.ingredients[1].unit == "chop"}})
    @@assert({{this.ingredients[2].unit == "pound"}})
}
