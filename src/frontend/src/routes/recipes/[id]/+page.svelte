<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { renderMarkdown } from "$lib/markdown";

  interface RecipeIngredient {
    name: string;
    quantity: string;
    unit: string;
    preparation: string | null;
    notes: string | null;
  }

  interface ClaimSummary {
    ingredient_name: string;
    quantity: number;
    unit: string;
    inventory_item_id: number;
  }

  interface Recipe {
    id: string;
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

  interface PageData {
    recipe: Recipe;
  }

  let { data }: { data: PageData } = $props();
  let recipe = $derived(data.recipe);
  let sessionId = $derived($page.url.searchParams.get("session") || "");
  let processing = $state(false);

  async function handleCook() {
    if (processing) return;
    processing = true;

    try {
      const response = await fetch(`/api/recipes/${recipe.id}/cook`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Cook failed: ${response.status}`);
      }

      // Navigate back to session page
      if (sessionId) {
        goto(`/sessions/${sessionId}`);
      } else {
        window.history.back();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to mark recipe as cooked";
      alert(message);
    } finally {
      processing = false;
    }
  }

  async function handleAbandon() {
    if (processing) return;
    processing = true;

    try {
      const response = await fetch(`/api/recipes/${recipe.id}/abandon`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Abandon failed: ${response.status}`);
      }

      // Navigate back to session page
      if (sessionId) {
        goto(`/sessions/${sessionId}`);
      } else {
        window.history.back();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to abandon recipe";
      alert(message);
    } finally {
      processing = false;
    }
  }

  function handleBack() {
    if (sessionId) {
      goto(`/sessions/${sessionId}`);
    } else {
      window.history.back();
    }
  }
</script>

<div class="container mx-auto p-6 max-w-4xl">
  <div class="mb-4">
    <button onclick={handleBack} class="btn preset-outlined-surface-500 btn-sm">
      ← Back
    </button>
  </div>

  <div class="card preset-outlined-primary-500 p-6 space-y-6">
    <div class="flex items-start justify-between">
      <h1 class="h2">{recipe.name}</h1>
      <div class="text-sm text-surface-500 text-right">
        <div>{recipe.active_time_minutes} min active</div>
        <div>{recipe.total_time_minutes} min total</div>
      </div>
    </div>

    <p class="text-surface-600-400">{recipe.description}</p>

    <div class="grid md:grid-cols-2 gap-6">
      <div>
        <h2 class="h4 mb-3">Ingredients ({recipe.servings} servings)</h2>
        <ul class="space-y-2">
          {#each recipe.ingredients as ingredient}
            <li class="text-sm">
              {ingredient.quantity}
              {ingredient.unit}
              {ingredient.name}{#if ingredient.preparation}, {ingredient.preparation}{/if}
            </li>
          {/each}
        </ul>
      </div>

      <div>
        <h2 class="h4 mb-3">Instructions</h2>
        <ol class="space-y-3 list-decimal list-inside">
          {#each recipe.instructions as step}
            <li class="text-sm">{@html renderMarkdown(step)}</li>
          {/each}
        </ol>
      </div>
    </div>

    {#if recipe.claims.length > 0}
      <div class="text-xs text-surface-500 pt-4 border-t border-surface-300-700">
        <span class="font-medium">Claimed from inventory:</span>
        {recipe.claims
          .map((c) => `${c.quantity} ${c.unit} ${c.ingredient_name}`)
          .join(", ")}
      </div>
    {/if}

    <div class="flex gap-3 pt-4 border-t border-surface-300-700">
      <button
        onclick={handleCook}
        class="btn preset-filled-success-500 flex-1"
        disabled={processing}
      >
        {processing ? "Processing..." : "Mark as Cooked"}
      </button>
      <button
        onclick={handleAbandon}
        class="btn preset-outlined-surface-500 flex-1"
        disabled={processing}
      >
        {processing ? "Processing..." : "Abandon"}
      </button>
    </div>
  </div>
</div>
