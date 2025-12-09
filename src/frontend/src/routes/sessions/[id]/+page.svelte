<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";

  interface Session {
    id: string;
    name: string;
    created_at: string;
  }

  interface Criterion {
    id: string;
    description: string;
    slots: number;
    created_at: string;
  }

  interface PitchIngredient {
    name: string;
    quantity: number;
    unit: string;
  }

  interface RecipeIngredient {
    name: string;
    quantity: string;
    unit: string;
    preparation: string | null;
    notes: string | null;
    purchase_likelihood?: number;
  }

  interface ClaimSummary {
    ingredient_name: string;
    quantity: number;
    unit: string;
    inventory_item_id: number;
  }

  interface FleshedOutRecipe {
    id: string;
    criterion_id: string | null;
    name: string;
    description: string;
    ingredients: RecipeIngredient[];
    instructions: string[];
    active_time_minutes: number;
    total_time_minutes: number;
    servings: number;
    notes: string | null;
    state: string;
    claims: ClaimSummary[];
  }

  interface ShoppingListItem {
    ingredient_name: string;
    total_quantity: string;
    purchase_likelihood: number;
    used_in_recipes: string[];
  }

  interface ShoppingListResponse {
    grocery_items: ShoppingListItem[];
    pantry_staples: ShoppingListItem[];
  }

  interface Pitch {
    id: string;
    criterion_id: string;
    name: string;
    blurb: string;
    why_make_this: string;
    inventory_ingredients: PitchIngredient[];
    active_time_minutes: number;
    created_at: string;
  }

  let session: Session | null = $state(null);
  let criteria: Criterion[] = $state([]);
  let pitches: Pitch[] = $state([]);
  let loading = $state(true);
  let error = $state("");

  // Form state
  let newDescription = $state("");
  let newSlots = $state(1);
  let submitting = $state(false);

  // Generation state
  let generating = $state(false);
  let generationProgress = $state("");
  let generationError = $state("");

  // Flesh-out state
  let fleshingOut = $state(false);
  let fleshOutProgress = $state("");
  let fleshOutError = $state("");
  let plannedRecipes: FleshedOutRecipe[] = $state([]);

  // Shopping list state
  let shoppingList: ShoppingListResponse | null = $state(null);
  let loadingShoppingList = $state(false);
  let shoppingListError = $state("");

  let selectedPitchIds: Set<string> = $state(new Set());
  let fleshedOutPitchIds: Set<string> = $state(new Set());
  let selectedCount = $derived(selectedPitchIds.size);

  // Calculate if all meal slots are filled
  let allSlotsFilled = $derived(
    (() => {
      const totalSlots = criteria.reduce((sum, c) => sum + c.slots, 0);
      const plannedCount = plannedRecipes.length;
      return totalSlots > 0 && totalSlots === plannedCount;
    })()
  );

  function togglePitchSelection(pitchId: string) {
    if (selectedPitchIds.has(pitchId)) {
      selectedPitchIds.delete(pitchId);
    } else {
      selectedPitchIds.add(pitchId);
    }
    selectedPitchIds = new Set(selectedPitchIds);
  }

  function isPitchSelected(pitchId: string): boolean {
    return selectedPitchIds.has(pitchId);
  }

  function markPitchesAsFleshedOut(pitchIds: string[]) {
    for (const id of pitchIds) {
      fleshedOutPitchIds.add(id);
      selectedPitchIds.delete(id);
    }
    fleshedOutPitchIds = new Set(fleshedOutPitchIds);
    selectedPitchIds = new Set(selectedPitchIds);
  }

  function getSelectedPitches(): Pitch[] {
    return pitches.filter((p) => selectedPitchIds.has(p.id));
  }

  let pitchesByCriterion = $derived(() => {
    const grouped: Record<string, Pitch[]> = {};
    for (const pitch of pitches) {
      if (fleshedOutPitchIds.has(pitch.id)) continue;

      if (!grouped[pitch.criterion_id]) {
        grouped[pitch.criterion_id] = [];
      }
      grouped[pitch.criterion_id].push(pitch);
    }
    return grouped;
  });

  // Group recipes by criterion for inline display
  let recipesByCriterion = $derived(() => {
    const grouped: Record<string, FleshedOutRecipe[]> = {};
    for (const recipe of plannedRecipes) {
      if (!recipe.criterion_id) continue;

      if (!grouped[recipe.criterion_id]) {
        grouped[recipe.criterion_id] = [];
      }
      grouped[recipe.criterion_id].push(recipe);
    }
    return grouped;
  });

  async function loadSession() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}`);
    if (response.ok) {
      session = await response.json();
    } else if (response.status === 404) {
      error = "Session not found";
    } else {
      error = "Failed to load session";
    }
    loading = false;
  }

  async function loadCriteria() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria`);
    if (response.ok) {
      criteria = await response.json();
    }
  }

  async function loadPitches() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/pitches`);
    if (response.ok) {
      pitches = await response.json();
    }
  }

  async function loadPlannedRecipes() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/recipes`);
    if (response.ok) {
      plannedRecipes = await response.json();
    }
  }

  async function loadShoppingList() {
    if (plannedRecipes.length === 0) {
      shoppingList = { grocery_items: [], pantry_staples: [] };
      return;
    }

    loadingShoppingList = true;
    shoppingListError = "";

    const id = $page.params.id;
    try {
      const response = await fetch(`/api/sessions/${id}/shopping-list`);
      if (response.ok) {
        shoppingList = await response.json();
      } else if (response.status === 404) {
        shoppingListError = "Session not found";
      } else {
        shoppingListError = "Failed to load shopping list";
      }
    } catch (err) {
      shoppingListError =
        err instanceof Error ? err.message : "Failed to load shopping list";
    } finally {
      loadingShoppingList = false;
    }
  }

  async function addCriterion() {
    if (!newDescription.trim() || submitting) return;

    submitting = true;
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        description: newDescription.trim(),
        slots: newSlots,
      }),
    });

    if (response.ok) {
      newDescription = "";
      newSlots = 1;
      await loadCriteria();
    }
    submitting = false;
  }

  async function deleteCriterion(criterionId: string) {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria/${criterionId}`, {
      method: "DELETE",
    });
    if (response.ok) {
      await loadCriteria();
    }
  }

  async function generatePitches() {
    if (generating) return;

    generating = true;
    generationProgress = "Starting generation...";
    generationError = "";

    const id = $page.params.id;
    const eventSource = new EventSource(`/api/sessions/${id}/generate-pitches`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        generationError = data.message;
        generationProgress = "";
        generating = false;
        eventSource.close();
      } else if (data.complete) {
        generationProgress = data.message || "Generation complete!";
        generating = false;
        eventSource.close();
        setTimeout(() => {
          generationProgress = "";
        }, 2000);
      } else if (data.progress) {
        generationProgress = `Generating for "${data.criterion_description}" (${data.criterion_index} of ${data.total_criteria}) - ${data.generating_count} pitches...`;
      } else if (data.pitch) {
        // Accumulate pitch in real-time
        const newPitch: Pitch = {
          id: data.data.id,
          criterion_id: data.criterion_id,
          name: data.data.name,
          blurb: data.data.blurb,
          why_make_this: data.data.why_make_this,
          inventory_ingredients: data.data.inventory_ingredients,
          active_time_minutes: data.data.active_time_minutes,
          created_at: new Date().toISOString(),
        };
        pitches = [...pitches, newPitch];
        generationProgress = `Generated "${newPitch.name}" (${data.pitch_index} of ${data.total_for_criterion})`;
      }
    };

    eventSource.onerror = () => {
      generationError = "Connection lost. Please try again.";
      generationProgress = "";
      generating = false;
      eventSource.close();
    };
  }

  async function fleshOutSelected() {
    if (fleshingOut || selectedCount === 0) return;

    fleshingOut = true;
    fleshOutProgress = `Fleshing out ${selectedCount} recipe${selectedCount > 1 ? "s" : ""}...`;
    fleshOutError = "";

    const selectedPitches = getSelectedPitches();
    const pitchesToFleshOut = selectedPitches.map((p) => ({
      name: p.name,
      blurb: p.blurb,
      inventory_ingredients: p.inventory_ingredients,
      criterion_id: p.criterion_id,
    }));

    const id = $page.params.id;

    try {
      const response = await fetch(`/api/sessions/${id}/flesh-out-pitches`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pitches: pitchesToFleshOut }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const data = await response.json();

      // Add new recipes to planned list
      plannedRecipes = [...plannedRecipes, ...data.recipes];

      // Mark pitches as fleshed out (removes from display)
      markPitchesAsFleshedOut(selectedPitches.map((p) => p.id));

      // Load shopping list with new recipes
      await loadShoppingList();

      // Show success briefly
      fleshOutProgress = `Created ${data.recipes.length} recipe${data.recipes.length !== 1 ? "s" : ""}!`;
      setTimeout(() => {
        fleshOutProgress = "";
      }, 2000);

      // Report any errors from individual pitches
      if (data.errors && data.errors.length > 0) {
        fleshOutError = `Some pitches failed: ${data.errors.join(", ")}`;
      }
    } catch (err) {
      fleshOutError =
        err instanceof Error ? err.message : "Failed to flesh out recipes";
      fleshOutProgress = "";
    } finally {
      fleshingOut = false;
    }
  }

  async function cookRecipe(recipeId: string) {
    try {
      const response = await fetch(`/api/recipes/${recipeId}/cook`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Cook failed: ${response.status}`);
      }

      // Reload recipes to show updated state (cooked recipes stay visible)
      await loadPlannedRecipes();

      // Refresh shopping list
      await loadShoppingList();

      return true;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to mark recipe as cooked";
      alert(message);
      return false;
    }
  }

  async function abandonRecipe(recipeId: string) {
    try {
      const response = await fetch(`/api/recipes/${recipeId}/abandon`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Abandon failed: ${response.status}`);
      }

      // Remove recipe from planned list (optimistic update)
      plannedRecipes = plannedRecipes.filter((r) => r.id !== recipeId);

      // Refresh shopping list
      await loadShoppingList();

      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to abandon recipe";
      alert(message);
      return false;
    }
  }

  onMount(async () => {
    await loadSession();
    if (!error) {
      await loadCriteria();
      await loadPitches();
      await loadPlannedRecipes();
      await loadShoppingList();
    }
  });
</script>

<main class="p-10 space-y-6 max-w-2xl mx-auto">
  <a href="/" class="text-sm text-surface-600-400 hover:underline"
    >&larr; Back to Home</a
  >

  {#if loading}
    <p class="text-surface-600-400">Loading session...</p>
  {:else if error}
    <div class="card preset-outlined-error-500 p-6">
      <p>{error}</p>
    </div>
  {:else if session}
    <div class="flex items-center justify-between">
      <h1 class="h1">{session.name || "Untitled Session"}</h1>
    </div>

    <p class="text-sm text-surface-600-400">
      Created {new Date(session.created_at).toLocaleDateString()}
    </p>

    <!-- Meal Criteria -->
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Meal Criteria</h2>

      <!-- Add Criterion Form -->
      <form
        onsubmit={(e) => {
          e.preventDefault();
          addCriterion();
        }}
        class="space-y-3"
      >
        <div class="flex gap-3">
          <input
            type="text"
            bind:value={newDescription}
            placeholder="e.g., Quick weeknight meals"
            class="input flex-1"
            disabled={submitting}
          />
          <div class="flex items-center gap-2">
            <label for="slots" class="text-sm text-surface-600-400">Slots:</label>
            <input
              id="slots"
              type="number"
              bind:value={newSlots}
              min="1"
              max="7"
              class="input w-16 text-center"
              disabled={submitting}
            />
          </div>
        </div>
        <button
          type="submit"
          class="btn preset-filled-primary-500"
          disabled={!newDescription.trim() || submitting}
        >
          Add Criterion
        </button>
      </form>

      <!-- Criteria List -->
      {#if criteria.length > 0}
        <ul class="space-y-2 mt-4">
          {#each criteria as criterion}
            <li
              class="flex items-center justify-between p-3 rounded bg-surface-100-900"
            >
              <div>
                <span class="font-medium">{criterion.description}</span>
                <span class="text-sm text-surface-600-400 ml-2">
                  ({criterion.slots}
                  {criterion.slots === 1 ? "slot" : "slots"})
                </span>
              </div>
              <button
                onclick={() => deleteCriterion(criterion.id)}
                class="btn btn-sm preset-outlined-error-500"
                aria-label="Delete criterion"
              >
                Delete
              </button>
            </li>
          {/each}
        </ul>
      {:else}
        <p class="text-surface-600-400 text-sm">
          No criteria yet. Add criteria to define your meal planning constraints.
        </p>
      {/if}
    </div>

    <!-- My Planned Recipes -->
    {#if plannedRecipes.length > 0}
      <div class="card preset-outlined-primary-500 p-6 space-y-4">
        <h2 class="h3">My Planned Recipes</h2>
        <div class="grid gap-3">
          {#each plannedRecipes as recipe}
            <div
              class="card p-4 space-y-3
                {recipe.state === 'cooked'
                ? 'preset-outlined-success-500 bg-success-500/5'
                : 'preset-outlined-success-500 bg-success-500/10'}"
            >
              <!-- Clickable area for navigation -->
              <button
                type="button"
                onclick={() =>
                  (window.location.href = `/recipes/${recipe.id}?session=${$page.params.id}`)}
                class="w-full text-left space-y-2"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-center gap-2">
                    <!-- Recipe indicator icon -->
                    <span
                      class="w-5 h-5 rounded-full bg-success-500 text-white flex items-center justify-center flex-shrink-0"
                    >
                      <svg
                        class="w-3 h-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="3"
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </span>
                    <h4 class="font-semibold text-lg">{recipe.name}</h4>
                    {#if recipe.state === "cooked"}
                      <span
                        class="text-xs px-2 py-1 rounded-full bg-success-500 text-white"
                      >
                        Cooked ✓
                      </span>
                    {/if}
                  </div>
                  <span class="text-sm text-surface-500">
                    {recipe.active_time_minutes} min
                  </span>
                </div>

                {#if recipe.claims.length > 0}
                  <p class="text-xs text-surface-600-400">
                    <span class="font-medium">From inventory:</span>
                    {recipe.claims
                      .map((c) => `${c.quantity} ${c.unit} ${c.ingredient_name}`)
                      .join(", ")}
                  </p>
                {/if}
              </button>

              <!-- Action buttons -->
              {#if recipe.state !== "cooked"}
                <div class="flex gap-2 pt-2 border-t border-surface-300-700">
                  <button
                    onclick={() => cookRecipe(recipe.id)}
                    class="btn btn-sm preset-filled-success-500 flex-1"
                  >
                    Mark as Cooked
                  </button>
                  <button
                    onclick={() => abandonRecipe(recipe.id)}
                    class="btn btn-sm preset-outlined-surface-500 flex-1"
                  >
                    Abandon
                  </button>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Shopping List -->
    {#if shoppingList && (shoppingList.grocery_items.length > 0 || shoppingList.pantry_staples.length > 0)}
      <div class="card preset-outlined-secondary-500 p-6 space-y-4">
        <h2 class="h3">Shopping List</h2>

        {#if loadingShoppingList}
          <p class="text-surface-600-400 text-sm">Loading shopping list...</p>
        {:else if shoppingListError}
          <div class="card preset-outlined-error-500 p-4">
            <p class="text-sm text-error-500">{shoppingListError}</p>
          </div>
        {:else}
          <!-- Grocery Items (high confidence) -->
          {#if shoppingList.grocery_items.length > 0}
            <div class="space-y-2">
              <h3 class="font-semibold text-surface-700-300">
                Grocery Items
                <span class="text-sm font-normal text-surface-500">
                  (High confidence - definitely need to buy)
                </span>
              </h3>
              <ul class="space-y-2">
                {#each shoppingList.grocery_items as item}
                  <li class="p-3 rounded bg-surface-100-900">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <span class="font-medium">{item.ingredient_name}</span>
                        <span class="text-surface-600-400 ml-2">
                          {item.total_quantity}
                        </span>
                      </div>
                      <span
                        class="text-xs px-2 py-1 rounded bg-primary-500/20 text-primary-500"
                      >
                        {Math.round(item.purchase_likelihood * 100)}% confidence
                      </span>
                    </div>
                    {#if item.used_in_recipes.length > 0}
                      <div class="text-xs text-surface-500 mt-1">
                        Used in: {item.used_in_recipes.join(", ")}
                      </div>
                    {/if}
                  </li>
                {/each}
              </ul>
            </div>
          {/if}

          <!-- Pantry Staples (low confidence) -->
          {#if shoppingList.pantry_staples.length > 0}
            <div class="space-y-2 pt-4 border-t border-surface-300-700">
              <h3 class="font-semibold text-surface-700-300">
                Pantry Staples to Verify
                <span class="text-sm font-normal text-surface-500">
                  (Lower confidence - check if you have these)
                </span>
              </h3>
              <ul class="space-y-2">
                {#each shoppingList.pantry_staples as item}
                  <li class="p-3 rounded bg-surface-100-900 opacity-75">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <span class="font-medium">{item.ingredient_name}</span>
                        <span class="text-surface-600-400 ml-2">
                          {item.total_quantity}
                        </span>
                      </div>
                      <span
                        class="text-xs px-2 py-1 rounded bg-surface-500/20 text-surface-500"
                      >
                        {Math.round(item.purchase_likelihood * 100)}% confidence
                      </span>
                    </div>
                    {#if item.used_in_recipes.length > 0}
                      <div class="text-xs text-surface-500 mt-1">
                        Used in: {item.used_in_recipes.join(", ")}
                      </div>
                    {/if}
                  </li>
                {/each}
              </ul>
            </div>
          {/if}
        {/if}
      </div>
    {/if}

    <!-- Recipe Pitch Generation -->
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Recipe Pitches</h2>
      {#if criteria.length === 0}
        <p class="text-surface-600-400">
          Add at least one criterion to generate recipe pitches.
        </p>
      {:else}
        <p class="text-surface-600-400">
          Ready to generate pitches for {criteria.length}
          {criteria.length === 1 ? "criterion" : "criteria"}.
        </p>
        <div class="flex gap-3 flex-wrap">
          <button
            class="btn preset-filled-secondary-500"
            disabled={generating || allSlotsFilled}
            onclick={generatePitches}
          >
            {#if generating}
              Generating...
            {:else if allSlotsFilled}
              All Meals Planned
            {:else}
              Generate Pitches
            {/if}
          </button>

          {#if selectedCount > 0}
            <button
              class="btn preset-filled-primary-500"
              disabled={generating || fleshingOut}
              onclick={fleshOutSelected}
            >
              {fleshingOut ? "Fleshing Out..." : "Flesh Out Selected"}
              <span
                class="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-sm font-medium"
              >
                {selectedCount}
              </span>
            </button>
          {/if}
        </div>

        {#if fleshOutProgress}
          <div class="card preset-outlined-primary-500 p-4">
            <p class="text-sm">{fleshOutProgress}</p>
          </div>
        {/if}

        {#if fleshOutError}
          <div class="card preset-outlined-error-500 p-4">
            <p class="text-sm text-error-500">{fleshOutError}</p>
          </div>
        {/if}

        {#if generationProgress}
          <div class="card preset-outlined-primary-500 p-4">
            <p class="text-sm">{generationProgress}</p>
          </div>
        {/if}

        {#if generationError}
          <div class="card preset-outlined-error-500 p-4">
            <p class="text-sm text-error-500">{generationError}</p>
          </div>
        {/if}

        <!-- Pitches and recipes grouped by criterion -->
        {#each criteria as criterion}
          {@const criterionPitches = pitchesByCriterion()[criterion.id] || []}
          {@const criterionRecipes = recipesByCriterion()[criterion.id] || []}
          {@const totalItems = criterionPitches.length + criterionRecipes.length}
          <div class="space-y-3 mt-6">
            <h3 class="h4 text-surface-700-300">
              {criterion.description}
              <span class="text-sm font-normal text-surface-500">
                ({criterionRecipes.length} planned, {criterionPitches.length} / {criterion.slots *
                  3} pitches)
              </span>
            </h3>

            {#if totalItems === 0}
              <p class="text-sm text-surface-500 italic">No pitches or recipes yet</p>
            {:else}
              <div class="grid gap-3">
                <!-- Show recipes first (planned meals) -->
                {#each criterionRecipes as recipe}
                  <button
                    type="button"
                    onclick={() =>
                      (window.location.href = `/recipes/${recipe.id}?session=${$page.params.id}`)}
                    class="card p-4 space-y-2 text-left w-full transition-all cursor-pointer
                      {recipe.state === 'cooked'
                      ? 'preset-outlined-success-500 bg-success-500/5'
                      : 'preset-outlined-success-500 bg-success-500/10 hover:bg-success-500/15'}"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex items-center gap-2">
                        <!-- Recipe indicator icon -->
                        <span
                          class="w-5 h-5 rounded-full bg-success-500 text-white flex items-center justify-center flex-shrink-0"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="3"
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        </span>
                        <h4 class="font-semibold text-lg">{recipe.name}</h4>
                        {#if recipe.state === "cooked"}
                          <span
                            class="text-xs px-2 py-1 rounded-full bg-success-500 text-white"
                          >
                            Cooked ✓
                          </span>
                        {/if}
                      </div>
                      <span class="text-sm text-surface-500">
                        {recipe.active_time_minutes} min
                      </span>
                    </div>
                    {#if recipe.claims.length > 0}
                      <p class="text-xs text-surface-600-400">
                        <span class="font-medium">From inventory:</span>
                        {recipe.claims
                          .map((c) => `${c.quantity} ${c.unit} ${c.ingredient_name}`)
                          .join(", ")}
                      </p>
                    {/if}
                  </button>
                {/each}

                <!-- Then show remaining pitches -->
                {#each criterionPitches as pitch}
                  <button
                    type="button"
                    onclick={() => togglePitchSelection(pitch.id)}
                    class="card p-4 space-y-2 text-left w-full transition-all cursor-pointer
                      {isPitchSelected(pitch.id)
                      ? 'preset-outlined-primary-500 ring-2 ring-primary-500 bg-primary-500/10'
                      : 'preset-outlined-surface-500 hover:bg-surface-100-900'}"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex items-center gap-2">
                        <span
                          class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0
                            {isPitchSelected(pitch.id)
                            ? 'border-primary-500 bg-primary-500 text-white'
                            : 'border-surface-400'}"
                        >
                          {#if isPitchSelected(pitch.id)}
                            <svg
                              class="w-3 h-3"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="3"
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          {/if}
                        </span>
                        <h4 class="font-semibold text-lg">{pitch.name}</h4>
                      </div>
                      <span class="text-sm text-surface-500">
                        {pitch.active_time_minutes} min
                      </span>
                    </div>
                    <p class="text-surface-600-400 italic">{pitch.blurb}</p>
                    <p class="text-sm text-surface-600-400">{pitch.why_make_this}</p>
                    {#if pitch.inventory_ingredients.length > 0}
                      <div class="text-sm">
                        <span class="font-medium">Uses:</span>
                        {pitch.inventory_ingredients
                          .map((i) => `${i.quantity} ${i.unit} ${i.name}`)
                          .join(", ")}
                      </div>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</main>
