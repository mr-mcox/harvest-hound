class Ingredient {
    name string
    quantity float
    unit string
}

function ExtractIngredients(text: string) -> Ingredient[] {
    client "openai/gpt-4.1-nano"
    prompt #"
        This text contains a list of ingredients.
        <text>
        {{ text }}
        </text>

        Extract the ingredients from the text.
        Normalize with these guidelines
        <guidelines>
        <ingredient>
        - Are singular and lowercase
        </ingredient>
        <unit>
        - Use full names
        - Are singular and lowercase
        - If unspecified, use the most reasonable unit
        </unit>
        <quantity>
        - If unspecified, use a reasonable quantity one would purchase
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
