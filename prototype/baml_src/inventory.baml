class Ingredient {
    name string
    quantity float
    unit string

    @@assert(positive_quantity, {{ this.quantity > 0 }})
    @@assert(name_not_empty, {{ this.name|length > 0 }})
    @@assert(unit_not_empty, {{ this.unit|length > 0 }})
}

class InventoryParsingResult {
    ingredients Ingredient[]
    parsing_notes string?
}

function ExtractIngredients(text: string) -> InventoryParsingResult {
    client "openai/gpt-4o-mini"
    prompt #"
        This text contains a list of ingredients for a grocery/food inventory system.
        <text>
        {{ text }}
        </text>

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
        - Use full names (pound, ounce, cup, tablespoon, teaspoon, bunch, head, etc.)
        - Are singular and lowercase
        - If unspecified, use the most reasonable unit for that ingredient
        </unit>
        <quantity>
        - If unspecified, use a reasonable quantity one would purchase
        - Always use numbers, never words (2 not "two")
        </quantity>
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
    }
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[0].quantity == 2}})
    @@assert({{this.ingredients[0].unit == "pound"}})
}

test kale_with_bunch {
    functions [ExtractIngredients]
    args {
        text "1 bunch kale"
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
    }
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[0].quantity == 2}})
    @@assert({{this.ingredients[0].unit == "pound"}})
}

test empty_input {
    functions [ExtractIngredients]
    args {
        text ""
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
    }
    @@assert({{this.ingredients|length == 2}})
    @@assert({{this.ingredients[0].name == "carrot"}})
    @@assert({{this.ingredients[1].name == "kale"}})
    @@assert({{this.parsing_notes != null}})
}
