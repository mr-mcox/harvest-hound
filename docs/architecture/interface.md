# Interface Contract

## 1 · Guiding Rules

| Principle                                | Rationale                                                                                                        |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| **HTTP = commands & queries**            | Anything that *asks* the system to do something or retrieves a point-in-time view is a synchronous REST call.    |
| **WebSocket = facts**                    | Every domain event that survives the Outbox is fanned-out to clients that have subscribed, providing an eventually-consistent UI. |
| **Event names mirror domain events**     | We reuse canonical names (`RecipeProposed`, `IngredientClaimed`, etc.) from the DDD doc to avoid vocabulary drift. |
| **All payloads are lean**                | Typed identifiers + flexible JSON blobs, aligning with the minimal-schema philosophy.                            |

---

## 2 · REST Endpoints (v0)

### 2.1 Inventory & Stores

| Verb   | Path                         | Body / Params                     | Purpose                                                         |
|--------|------------------------------|-----------------------------------|-----------------------------------------------------------------|
| GET    | `/stores`                    | –                                 | List stores with denormalized view (item_count included)        |
| POST   | `/stores`                    | `{name, description?, infinite_supply?}` | Create a new store                                              |
| PUT    | `/stores/{storeId}`          | `{priority?, name?}`              | Edit store metadata                                             |
| DELETE | `/stores/{storeId}`          | –                                 | Remove a store                                                  |
| POST   | `/stores/{storeId}/inventory`| `{inventory_text: string}`        | Bulk add inventory; backend parses using LLM                    |
| GET    | `/stores/{storeId}/inventory`| –                                 | Get denormalized inventory items (includes ingredient_name, store_name) |
| GET    | `/inventory/current`         | `?storeId=`                       | Projection of current inventory for UI                          |

### 2.2 Planning Sessions

| Verb   | Path                                | Body / Params                                   | Purpose                                            |
|--------|-------------------------------------|-------------------------------------------------|----------------------------------------------------|
| POST   | `/meal-plans`                       | `MealPlanSpec` (natural-language)               | Start a new planning session (returns `planId`)   |
| GET    | `/meal-plans/{planId}`              | –                                               | Snapshot of the current plan                      |
| POST   | `/meal-plans/{planId}/feedback`     | `{recipeId, action: "approve" \| "reject"}`     | Submit user feedback on a proposed recipe         |
| POST   | `/meal-plans/{planId}/finalise`     | –                                               | Commit all accepted claims & close the session     |
| DELETE | `/meal-plans/{planId}`              | –                                               | Abort the session (emits `PlanDiscarded`)         |

### 2.3 Recipe Details

| Verb | Path                              | Purpose                                  |
|------|-----------------------------------|------------------------------------------|
| GET  | `/recipes/{recipeId}`             | Retrieve full recipe (draft or final)    |
| GET  | `/recipes/{recipeId}/lineage`     | Get the recipe’s revision history tree   |

### 2.4 Convenience Queries

| Path                         | Purpose                                        |
|------------------------------|------------------------------------------------|
| `/shopping-lists/{planId}`   | Aggregated shopping list projection            |
| `/prep-timeline/{planId}`    | Day-of-cooking timeline (future feature)       |

---

## 3 · Response Models (Read Models)

The API uses denormalized read models optimized for UI consumption. These eliminate N+1 queries and reduce frontend complexity.

### 3.1 Store View Model

```typescript
interface StoreListItem {
  store_id: string;
  name: string;
  description: string;
  item_count: number;  // Computed from inventory items
}
```

### 3.2 Inventory Item View Model

```typescript
interface InventoryItem {
  store_id: string;
  ingredient_id: string;
  ingredient_name: string;  // Denormalized from ingredient
  store_name: string;       // Denormalized from store
  quantity: number;
  unit: string;
  notes?: string;
  added_at: string;         // ISO timestamp
}
```

These models are maintained by event projections that update denormalized views whenever domain events occur.

---

## 4 · WebSocket API

### 4.1 Endpoint & Handshake

```
ws://{host}/ws?planId={planId}&storeIds=all
```

_Query parameters are server-side filters so clients only receive relevant events._

**Client “subscribe” message:**

```json
{
  "type": "subscribe",
  "planId": "123e4567...",
  "storeIds": ["perishables","freezer"]
}
```

_Server ack:_

```json
{"type":"subscribed","heartbeat":30}
```

### 4.2 Event Envelope

```json
{
  "type": "domain_event",
  "event": "RecipeProposed",
  "ts": "2025-06-29T21:02:11Z",
  "payload": { /* event-specific fields */ }
}
```

### 4.3 Event Catalogue (v0)

| Event                          | Sent When                       | Payload Fields                                  |
|--------------------------------|---------------------------------|-------------------------------------------------|
| `IngredientAddedToStore`       | After inventory upload          | `storeId, ingredientId, qty`                   |
| `IngredientClaimed` / `IngredientClaimReleased` | Planner reserves/releases items | `claimId, mealId, items[]`                    |
| `RecipeProposed`               | Planner emits a new recipe pitch| `planId, recipeId, summary, blockingItems[]`   |
| `ClaimAccepted` / `ClaimPartial` | Broker replies                 | `claimId, missing[]?`                          |
| `UserFeedbackReceived`         | On REST feedback save           | `recipeId, action`                             |
| `RecipeFinalised`              | When full recipe is generated   | `recipeId, instructionsURL`                    |
| `MealPlanFinalised`            | On user finalisation            | `planId, shoppingListURL`                      |

---

## 5 · Interface Sequence (Happy Path)

1. **POST** `/meal-plans` → `201 Created` + `planId`.
2. Front end opens **WS** `ws://.../ws?planId={planId}`.
3. Server streams `RecipeProposed` events.
4. User clicks “Approve” → **POST** `/meal-plans/{planId}/feedback`.
5. Broker emits `IngredientClaimed` or `ClaimPartial` → streamed.
6. User **POST** `/meal-plans/{planId}/finalise`.
7. Server emits `MealPlanFinalised` → client redirects to `/shopping-lists/{planId}`.
