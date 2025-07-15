class Ingredient {
    name string
    quantity float
    unit string

    @@assert(positive_quantity, {{ this.quantity > 0 }})
    @@assert(name_not_empty, {{ this.name|length > 0 }})
    @@assert(unit_not_empty, {{ this.unit|length > 0 }})
}

function ExtractIngredients(text: string) -> Ingredient[] {
    client "openai/gpt-4.1-mini"
    prompt #"
        This text contains a list of ingredients.
        <text>
        {{ text }}
        </text>

        Extract the ingredients from the text. If the text is empty or contains no ingredients, return an empty list.

        Normalize with these guidelines:
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
    @@assert({{this[0].name == "carrot"}})
    @@assert({{this[0].quantity == 2}})
    @@assert({{this[0].unit == "pound"}})
}

test kale_with_bunch {
    functions [ExtractIngredients]
    args {
        text "1 bunch kale"
    }
    @@assert({{this[0].name == "kale"}})
    @@assert({{this[0].quantity == 1}})
    @@assert({{this[0].unit == "bunch"}})
}

test multi_line_ingredients {
    functions [ExtractIngredients]
    args {
        text #"
        2 lbs carrots
        1 bunch kale
        "#
    }
    @@assert({{this|length == 2}})
    @@assert({{this[0].name == "carrot"}})
    @@assert({{this[1].name == "kale"}})
}

test carrots_rice {
    functions [ExtractIngredients]
    args {
        text #"
        - 2 lbs carrots\n- 1/2 cup rice
        "#
    }
    @@assert({{this[0].name == "carrot"}})
    @@assert({{this[0].quantity == 2}})
    @@assert({{this[0].unit == "pound"}})
    @@assert({{this[1].name == "rice"}})
    @@assert({{this[1].quantity == 0.5}})
    @@assert({{this[1].unit == "cup"}})
}

test csv_format {
    functions [ExtractIngredients]
    args {
        text "carrots, 2, lbs"
    }
    @@assert({{this[0].name == "carrot"}})
    @@assert({{this[0].quantity == 2}})
    @@assert({{this[0].unit == "pound"}})
}

test empty_input {
    functions [ExtractIngredients]
    args {
        text ""
    }
    @@assert({{this|length == 0}})
}
