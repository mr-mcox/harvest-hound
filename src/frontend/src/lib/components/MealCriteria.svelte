<script lang="ts">
  interface Criterion {
    id: string;
    description: string;
    slots: number;
    created_at: string;
  }

  interface Props {
    sessionId: string;
    criteria: Criterion[];
    onUpdate: () => Promise<void>;
  }

  let { sessionId, criteria, onUpdate }: Props = $props();

  let newDescription = $state("");
  let newSlots = $state(1);
  let submitting = $state(false);

  async function addCriterion() {
    if (!newDescription.trim() || submitting) return;

    submitting = true;
    const response = await fetch(`/api/sessions/${sessionId}/criteria`, {
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
      await onUpdate();
    }
    submitting = false;
  }

  async function deleteCriterion(criterionId: string) {
    const response = await fetch(`/api/sessions/${sessionId}/criteria/${criterionId}`, {
      method: "DELETE",
    });
    if (response.ok) {
      await onUpdate();
    }
  }
</script>

<div class="card preset-outlined-surface-500 p-6 space-y-4">
  <h3 class="h4">Meal Criteria</h3>

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
        <li class="flex items-center justify-between p-3 rounded bg-surface-100-900">
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
