# Opportunity Brief: Description-Based Store Model

**Problem Statement**

The current binary "infinite supply" model doesn't adequately represent real-world ingredient sources like pantries and grocery stores. These stores don't have enumerated inventories but rather represent categories of ingredient availability that the RecipePlanner should understand and leverage during meal planning.

Evidence from user feedback:
- "The 'infinite supply' is all wrong. It's not about infinite supply vs not"
- "Instead of presenting a list of ingredients, it presents a description of what that infinite supply contains (eg 'anything reasonably found at a Cub grocery store') that can be used to craft recipes"
- Need to distinguish between stores with concrete inventories (CSA deliveries) and stores with conceptual availability (grocery stores, pantries)

**User Stories**

**Story 1: Grocery Store Reference**
As a user setting up my ingredient sources, I want to define my local grocery store as "anything typically found at a full-service grocery store" so that the meal planner can suggest recipes knowing I can purchase missing ingredients without me having to list thousands of possible items.

**Story 2: Specialized Pantry**
As a user with a well-stocked baking pantry, I want to describe it as "comprehensive baking ingredients including specialty flours, extracts, and decorating supplies" so that the RecipePlanner can confidently suggest complex baking recipes.

**Story 3: Recipe Planning Integration**
As a user planning meals, I want the RecipePlanner to understand that my "Asian grocery store" can provide specialized ingredients like miso, kombu, and specialty sauces so that it can suggest authentic recipes even if those ingredients aren't in my current CSA delivery.

**Current Experience**

1. User creates store with "infinite supply" checkbox
2. System treats infinite supply as binary on/off
3. No way to communicate what that infinite supply contains
4. RecipePlanner has no context about store capabilities
5. Users must manually enumerate items or RecipePlanner can't leverage store

**Impact**: RecipePlanner can't effectively use backup ingredient sources, leading to conservative recipe suggestions and missed meal planning opportunities.

**Desired Outcomes**

**User Success**:
- Different store types feel appropriate to their real-world counterparts
- RecipePlanner can confidently suggest recipes leveraging described store capabilities
- Users can express nuanced ingredient availability without enumeration

**Measurable Impact**:
- Increase recipe variety when users have grocery/pantry stores defined
- Reduce "ingredient not available" constraints in meal planning
- Enable more adventurous recipe suggestions based on store descriptions

**Behavioral Change**:
- Users describe their ingredient ecosystem more completely
- RecipePlanner suggests recipes it previously couldn't due to ingredient uncertainty
- System better matches real-world ingredient sourcing patterns

**Non-Goals**:
- Real-time grocery store inventory integration
- Price comparison or shopping list optimization
- Detailed categorization systems for store types

**Constraints & Considerations**

**Must Preserve**:
- Existing concrete inventory stores (CSA, freezer deliveries) continue to work as enumerated lists
- Event sourcing patterns for store changes
- IngredientBroker claiming logic for concrete inventories

**Business Rules**:
- Description-based stores cannot have concrete ingredient claims (no reservations)
- RecipePlanner must understand store descriptions as availability context
- Different claiming behavior for description-based vs inventory-based stores

**User Expectations**:
- Grocery stores represent "things I can buy"
- Pantries represent "things I have categories of"
- Description text should be natural language, not structured data
- RecipePlanner should "understand" store descriptions intelligently

**Technical Boundaries**:
- Must integrate with existing InventoryStore aggregate
- Maintain domain separation between ingredient claiming and availability description
- Support within current BAML/LLM integration patterns

**Related Opportunities**

- **Streamlined Store Creation UX**: Complementary opportunity addressing workflow and presentation
- **Recipe Planning Intelligence**: How well RecipePlanner interprets store descriptions affects value
- **Ingredient Normalization**: Store descriptions may reference ingredients not in canonical database

**Open Questions**

1. **Domain Modeling**: Should description-based stores be a different aggregate type, or a variant of InventoryStore with different behavior?

2. **RecipePlanner Integration**: How should store descriptions be passed to RecipePlanner? As context during recipe generation? As part of ingredient availability queries?

3. **Claiming Behavior**: How does IngredientBroker handle "claims" against description-based stores? Should they always succeed? Generate purchase/shopping tasks?

4. **Description Quality**: How do we guide users toward effective descriptions that RecipePlanner can interpret well?

5. **Hybrid Stores**: Should stores support both description AND concrete inventory? (e.g., "Well-stocked pantry" + specific specialty items enumerated)

6. **Store Templates**: Would predefined description templates ("Full-Service Grocery", "Asian Specialty Store", "Baking Pantry") help users while maintaining flexibility?

**Success Criteria**

- Users can define stores using natural language descriptions
- RecipePlanner generates more diverse recipes when description-based stores are available
- System clearly differentiates between concrete inventory and described availability
- Store descriptions feel intuitive and match real-world ingredient sourcing patterns