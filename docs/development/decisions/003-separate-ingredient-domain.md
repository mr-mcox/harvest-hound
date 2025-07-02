# Separate Ingredient Bounded Context

## Context and Problem Statement

Ingredient-related logic appears across multiple areas: recipe parsing, inventory management, and meal planning negotiation. We need to decide whether ingredient normalization, matching, and unit conversion should live within existing bounded contexts (Inventory, Recipe, Planning) or form a separate Ingredient domain. This affects system modularity, evolution flexibility, and separation of concerns.

## Considered Options

* Ingredient logic within Inventory bounded context
* Ingredient logic within Recipe bounded context
* Ingredient logic distributed across multiple contexts
* Separate Ingredient bounded context

## Decision Outcome

Chosen option: "Separate Ingredient bounded context", because ingredient normalization, matching, and unit conversion represent a rich domain concept that serves multiple consumers, can evolve independently, and deserves its own ubiquitous language and evolution path.

### Consequences

* Good, because ingredient logic can evolve independently (better LLM models, external data sources)
* Good, because multiple contexts can consume ingredient services without coupling
* Good, because clear ubiquitous language around ingredient operations ("normalize", "match", "convert")
* Good, because enables sophisticated ingredient intelligence (hierarchies, seasonal variations, regional names)
* Good, because anti-corruption layers provide clean integration boundaries
* Bad, because adds another bounded context to coordinate and maintain
* Bad, because potential over-engineering if ingredient logic remains simple
* Bad, because cross-context communication overhead for ingredient operations

## Implementation Details

**Ingredient Context responsibilities:**
- Ingredient aggregate (canonical representation)
- IngredientNormalizer service
- UnitConverter service
- IngredientMatcher service

**Context interactions:**
- Recipe Context uses Ingredient Context for parsing assistance
- Inventory Context uses Ingredient Context for normalization
- Planning Context coordinates between Recipe and Ingredient contexts

**Anti-corruption layers** translate between contexts, with each context maintaining its own view of ingredient data appropriate to its concerns.
