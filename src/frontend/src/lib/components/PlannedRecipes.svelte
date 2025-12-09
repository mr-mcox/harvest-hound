<script lang="ts">
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
    active_time_minutes: number;
    total_time_minutes: number;
    servings: number;
    notes: string | null;
    state: string;
    claims: ClaimSummary[];
  }

  interface Props {
    sessionId: string;
    plannedRecipes: FleshedOutRecipe[];
    onCook: (recipeId: string) => Promise<boolean>;
    onAbandon: (recipeId: string) => Promise<boolean>;
  }

  let { sessionId, plannedRecipes, onCook, onAbandon }: Props = $props();
</script>

{#if plannedRecipes.length > 0}
  <div class="card preset-outlined-primary-500 p-6 space-y-4">
    <h3 class="h4">My Planned Recipes</h3>
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
              (window.location.href = `/recipes/${recipe.id}?session=${sessionId}`)}
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
                onclick={() => onCook(recipe.id)}
                class="btn btn-sm preset-filled-success-500 flex-1"
              >
                Mark as Cooked
              </button>
              <button
                onclick={() => onAbandon(recipe.id)}
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
