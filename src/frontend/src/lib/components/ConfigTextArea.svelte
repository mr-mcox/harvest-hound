<script lang="ts">
  interface Props {
    label: string;
    apiEndpoint: string;
    initialContent: string;
  }

  let { label, apiEndpoint, initialContent }: Props = $props();

  // eslint-disable-next-line svelte/state-referenced-locally -- intentionally capture initial value only
  let content = $state(initialContent);
  let saving = $state(false);
  let saveStatus = $state<"idle" | "saved" | "error">("idle");
  let errorMessage = $state("");

  async function save() {
    saving = true;
    saveStatus = "idle";
    errorMessage = "";

    try {
      const response = await fetch(apiEndpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.status}`);
      }

      saveStatus = "saved";
      setTimeout(() => {
        saveStatus = "idle";
      }, 3000);
    } catch (e) {
      saveStatus = "error";
      errorMessage = e instanceof Error ? e.message : "Failed to save";
    } finally {
      saving = false;
    }
  }
</script>

<div class="space-y-2">
  <textarea
    class="textarea px-4 py-2 w-full"
    rows="4"
    placeholder={label}
    bind:value={content}
  ></textarea>
  <div class="flex items-center gap-4">
    <button
      type="button"
      class="btn preset-filled-primary-500"
      onclick={save}
      disabled={saving}
    >
      {saving ? "Saving..." : "Save"}
    </button>
    {#if saveStatus === "saved"}
      <span class="text-success-500">Saved</span>
    {/if}
    {#if saveStatus === "error"}
      <span class="text-error-500">{errorMessage}</span>
    {/if}
  </div>
</div>
