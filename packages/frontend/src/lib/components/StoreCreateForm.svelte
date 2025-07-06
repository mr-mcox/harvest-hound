<script lang="ts">
	import { validateStoreForm, type ValidationResult } from '$lib/validation.js';

	export let onSubmit: (data: {
		name: string;
		description: string;
		infinite_supply: boolean;
	}) => void = () => {};

	let name = '';
	let description = '';
	let infinite_supply = false;
	let error = '';

	function handleSubmit(event: Event) {
		event.preventDefault();

		const validation: ValidationResult = validateStoreForm({ name, description, infinite_supply });

		if ('error' in validation) {
			error = validation.error;
			return;
		}

		error = '';
		onSubmit({ name, description, infinite_supply });
	}
</script>

<div class="container mx-auto max-w-2xl p-4">
	<h1 class="mb-6 text-2xl font-bold">Create New Store</h1>

	<form on:submit={handleSubmit} class="space-y-4">
		<div class="form-control">
			<label class="label" for="name">
				<span class="label-text">Store Name</span>
			</label>
			<input
				id="name"
				type="text"
				bind:value={name}
				placeholder="e.g., CSA Box, Pantry, Freezer"
				class="input"
			/>
		</div>

		<div class="form-control">
			<label class="label" for="description">
				<span class="label-text">Description</span>
			</label>
			<textarea
				id="description"
				bind:value={description}
				placeholder="Optional description of this store"
				class="textarea"
				rows="3"
			></textarea>
		</div>

		<div class="form-control">
			<label class="label cursor-pointer justify-start gap-2" for="infinite_supply">
				<input
					id="infinite_supply"
					type="checkbox"
					bind:checked={infinite_supply}
					class="checkbox"
				/>
				<span class="label-text">Infinite Supply</span>
			</label>
		</div>

		{#if error}
			<div class="alert variant-filled-error">
				<div class="alert-message">
					<p>{error}</p>
				</div>
			</div>
		{/if}

		<div class="flex gap-4">
			<button type="submit" class="btn variant-filled-primary">Create Store</button>
			<a href="/stores" class="btn variant-ghost">Cancel</a>
		</div>
	</form>
</div>
