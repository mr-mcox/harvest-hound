class Dish {
    name string
    description string
}

function NameDishes(ingredient: string) -> Dish[] {
    client Anthropic
    prompt #"
        Name three creative dishes that feature {{ ingredient }} as a key ingredient.

        For each dish, provide:
        - A catchy name
        - A brief description (1-2 sentences)

        {{ ctx.output_format }}
    "#
}
