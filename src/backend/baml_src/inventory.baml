enum Priority {
    Low
    Medium
    High
    Urgent
}

class Ingredient {
    name string
    quantity float
    unit string
    priority Priority
    portion_size string?

    @@assert(positive_quantity, {{ this.quantity > 0 }})
    @@assert(name_not_empty, {{ this.name|length > 0 }})
    @@assert(unit_not_empty, {{ this.unit|length > 0 }})
}

class InventoryParsingResult {
    ingredients Ingredient[]
    parsing_notes string?
}

function ExtractIngredients(text: string, configuration_instructions: string?) -> InventoryParsingResult {
    client OpenAI
    prompt #"
        Extract ingredients from this text for a grocery/food inventory system.

        <text>
        {{ text }}
        </text>

        {% if configuration_instructions %}
        <configuration_instructions>
        {{ configuration_instructions }}
        </configuration_instructions>

        Apply these configuration instructions when parsing the ingredients. They may specify portion sizes, priorities, or other context about the batch.
        {% endif %}

        Extract ONLY ingredients that appear in the text above. Do not add any ingredients that are not explicitly mentioned.

        Normalize ingredients with these guidelines:
        - name: singular, lowercase, include category context when nested (e.g., "pork butt roast" not just "butt roast")
        - quantity: numeric value (e.g., 2 not "two")
        - unit: full name, singular, lowercase (e.g., "pound" not "lbs", "cup" not "cups")
          - For countable items, use item-specific units: "roast", "chop", "can", "jar", "head", "bunch"
          - When you see "xN" notation (e.g., "x3"), N is the quantity and the item type is the unit
          - Avoid generic units like "piece", "each", "item" - be specific to what it is
        - priority: infer based on perishability (how quickly it will spoil)
          - Urgent: fresh items that spoil quickly (leafy greens, herbs, berries, fresh cream)
          - High: items to use relatively soon (other fresh vegetables, fresh meat)
          - Medium: default for most items (root vegetables, frozen meat, pantry staples)
          - Low: long shelf life (dried goods, canned items, frozen vegetables)
        - portion_size: extract if specified in text or configuration instructions
          - From text: "3 16oz cans" → "16 ounce"
          - From config: if config says "all in 1 pound portions", apply to relevant items
          - Use full unit names (e.g., "16 ounce" not "16oz", "1 pound" not "1lb")
          - Text-specified portions take precedence over config-specified portions
          - null if no portion size specified anywhere
          - The name should NOT include the container type (e.g., "black bean" not "black bean can")

        {{ ctx.output_format }}
    "#
}

test simple_units_carrots {
    functions [ExtractIngredients]
    args {
        text "2 lbs carrots"
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 1 }})
    @@assert({{ this.ingredients[0].name == "carrot" }})
    @@assert({{ this.ingredients[0].quantity == 2 }})
    @@assert({{ this.ingredients[0].unit == "pound" }})
}

test simple_units_kale_bunch {
    functions [ExtractIngredients]
    args {
        text "1 bunch kale"
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 1 }})
    @@assert({{ this.ingredients[0].name == "kale" }})
    @@assert({{ this.ingredients[0].quantity == 1 }})
    @@assert({{ this.ingredients[0].unit == "bunch" }})
}

test simple_units_multi_line {
    functions [ExtractIngredients]
    args {
        text #"
        2 lbs carrots
        1 bunch kale
        1/2 cup rice
        "#
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 3 }})
    @@assert({{ this.ingredients[0].name == "carrot" }})
    @@assert({{ this.ingredients[1].name == "kale" }})
    @@assert({{ this.ingredients[2].name == "rice" }})
    @@assert({{ this.ingredients[2].quantity == 0.5 }})
    @@assert({{ this.ingredients[2].unit == "cup" }})
}

test count_units_meat_x_notation {
    functions [ExtractIngredients]
    args {
        text #"
        - Pork
            - Butt Roast x3
            - Loin chops x4
        "#
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 2 }})
    @@assert({{ this.ingredients[0].name == "pork butt roast" }})
    @@assert({{ this.ingredients[0].quantity == 3 }})
    @@assert({{ this.ingredients[0].unit == "roast" }})
    @@assert({{ this.ingredients[1].name == "pork loin chop" }})
    @@assert({{ this.ingredients[1].quantity == 4 }})
    @@assert({{ this.ingredients[1].unit == "chop" }})
}

test priority_inference_perishability {
    functions [ExtractIngredients]
    args {
        text #"
        1 bunch spinach
        2 lbs carrots
        1 can black beans
        1 lb fresh chicken breast
        "#
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 4 }})
    // spinach is leafy green -> Urgent
    @@assert({{ this.ingredients[0].priority == "Urgent" }})
    // carrots are root vegetables -> Medium or High
    @@assert({{ this.ingredients[1].priority in ["Medium", "High"] }})
    // canned beans -> Low
    @@assert({{ this.ingredients[2].priority == "Low" }})
    // fresh chicken -> High
    @@assert({{ this.ingredients[3].priority == "High" }})
}

test portion_size_from_text {
    functions [ExtractIngredients]
    args {
        text #"
        3 16oz cans black beans
        4 1lb bags frozen peas
        "#
        configuration_instructions null
    }
    @@assert({{ this.ingredients|length == 2 }})
    // 3 cans, each 16oz
    @@assert({{ this.ingredients[0].name == "black bean" }})
    @@assert({{ this.ingredients[0].quantity == 3 }})
    @@assert({{ this.ingredients[0].unit == "can" }})
    @@assert({{ this.ingredients[0].portion_size == "16 ounce" }})
    // 4 bags, each 1lb
    @@assert({{ this.ingredients[1].name == "frozen pea" }})
    @@assert({{ this.ingredients[1].quantity == 4 }})
    @@assert({{ this.ingredients[1].unit == "bag" }})
    @@assert({{ this.ingredients[1].portion_size == "1 pound" }})
}

test portion_size_from_config {
    functions [ExtractIngredients]
    args {
        text #"
        Ground beef x5
        Chicken breast x3
        "#
        configuration_instructions "All meat is frozen in 1 pound portions"
    }
    @@assert({{ this.ingredients|length == 2 }})
    // Config says 1 pound portions for all meat
    @@assert({{ this.ingredients[0].name == "ground beef" }})
    @@assert({{ this.ingredients[0].quantity == 5 }})
    @@assert({{ this.ingredients[0].portion_size == "1 pound" }})
    @@assert({{ this.ingredients[1].name == "chicken breast" }})
    @@assert({{ this.ingredients[1].quantity == 3 }})
    @@assert({{ this.ingredients[1].portion_size == "1 pound" }})
}
