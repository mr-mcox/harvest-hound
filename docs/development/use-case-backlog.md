# High-Level Use Cases

## UC1: Create Inventory Store & Bulk-Upload Inventory

User-Facing Value
	•	User adds a new “Perishables” (or “Freezer,” etc.) store, then pastes or uploads a CSV of ingredients+quantities.
	•	Immediately sees the parsed list of ingredients under that store in the inventory view.
	•	LLM parsing creates new Ingredient entities dynamically for unknown items.

Technical Implementation
	•	Front end
	•	New “Add Store” form + CSV/text-paste widget.
	•	On submit:
		1.	POST /stores { type, name } → returns storeId
		2.	POST /stores/{storeId}/inventory { blob }
	•	Show loading / errors; then fetch /inventory/current?storeId= to render table.
	•	Back end
	•	Models: Store, InventoryItem (SQLModel/Pydantic).
	•	Endpoints:
	•	POST /stores → persist store.
	•	POST /stores/{storeId}/inventory → parse CSV/blob, upsert items.
	•	Events: emit IngredientAddedToStore(storeId, ingredientId, qty) for each line.
	•	Ingredient Context: creates canonical Ingredient entities, links InventoryItems via ingredient_id.
	•	WebSocket: broadcast those events to any subscribers.

## UC2: View & Refresh Current Inventory

User-Facing Value
	•	On Inventory page, user sees a live-updating list of all stores and their ingredients/quantities.
	•	As other sessions add items, the table updates without a manual refresh.

Technical Implementation
	•	Front end
	•	On mount, GET /stores + GET /inventory/current; render grouped table.
	•	Open WS ws://…/ws?storeIds=all and on each IngredientAddedToStore adjust the row’s qty.
	•	Back end
	•	Projection: maintain a read model CurrentInventoryView for fast GET /inventory/current.
	•	WebSocket hub: accept subscriptions with storeIds filter; push domain events.

## UC3: Start a Meal-Planning Session

User-Facing Value
	•	User clicks “Plan meals” and types “Mexican dinners for 5 nights.”
	•	A new blank plan opens, ready to show recipe suggestions.

Technical Implementation
	•	Front end
	•	“New Plan” modal → collect MealPlanSpec (text).
	•	POST /meal-plans { spec } → returns planId; navigate to /plans/{planId}.
	•	Open WS ?planId={planId}.
	•	Back end
	•	Endpoint: POST /meal-plans: create Plan aggregate, persist PlanCreated(planId,spec).
	•	Planner service: enqueue job to generate first recipe proposals.

## UC4: Stream & Display Recipe Proposals

User-Facing Value
	•	As the AI broker pitches recipes (“Taco Bowls,” “Enchiladas”), they appear one-by-one in the UI.
	•	Each proposal shows a summary, pic, and “approve / reject” buttons.

Technical Implementation
	•	Front end
	•	Subscribe to WS; on RecipeProposed{ planId, recipeId, summary, blockingItems } append card.
	•	Back end
	•	Recipe Materialization: convert stored recipes into normalized IngredientRequirement objects via Ingredient Context.
	•	Broker: negotiate using normalized ingredients, as each recipe is ready, emit RecipeProposed.
	•	WebSocket: fan out that event to the client’s plan subscription.

## UC5: Submit Feedback & Claim Ingredients

User-Facing Value
	•	Clicking “Approve” reserves the needed ingredients (or shows that some are missing).
	•	User sees a spinner or immediate claim result.

Technical Implementation
	•	Front end
	•	On approve: POST /meal-plans/{planId}/feedback { recipeId, action:"approve" }.
	•	Disable buttons; await subsequent WS events ClaimAccepted or ClaimPartial.
	•	Back end
	•	Endpoint: record UserFeedbackReceived; use materialized IngredientRequirements to invoke IngredientBroker.
	•	Broker negotiates using normalized ingredient data for accurate matching.
	•	Emit IngredientClaimed (or ClaimPartial{ missing }) domain event.
	•	Update CurrentInventoryView projection accordingly.

## UC6: Display Claim Results & Updated Inventory

User-Facing Value
	•	After approval, the recipe card shows “✓ Ingredients reserved” or “⚠️ 2 items missing.”
	•	The Inventory sidebar updates counts in real-time.

Technical Implementation
	•	Front end
	•	WS handler: on IngredientClaimed, update the recipe card’s status and inventory table.
	•	On ClaimPartial, highlight missing items and link to “Add to shopping list.”
	•	Back end
	•	Broadcast IngredientClaimed / IngredientClaimPartial with claimId, missing[].
	•	Projections adjust quantities or report shortages.

## UC7: Finalise Plan & Generate Shopping List

User-Facing Value
	•	User clicks “Finish planning,” and sees a consolidated shopping list PDF/download link.
	•	They get day-of prep steps (future enhancement).

Technical Implementation
	•	Front end
	•	POST /meal-plans/{planId}/finalise → await MealPlanFinalised { shoppingListURL }.
	•	Redirect to /shopping-lists/{planId}; render link or embed PDF viewer.
	•	Back end
	•	Endpoint: emit MealPlanFinalised; collate accepted claims into ShoppingListView; persist PDF/URL.
	•	WebSocket: send final event so any open plan views update accordingly.
