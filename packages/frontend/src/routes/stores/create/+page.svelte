<script lang="ts">
	import { goto } from '$app/navigation';
	import { apiPost } from '$lib/api';
	import StoreCreateForm from '$lib/components/StoreCreateForm.svelte';

	async function handleSubmit(data: { name: string; description: string; infinite_supply: boolean }) {
		try {
			const response = await apiPost('/stores', {
				name: data.name,
				description: data.description,
				infinite_supply: data.infinite_supply
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			// Success - redirect to stores list
			await goto('/stores');
		} catch (err) {
			// Let the component handle the error display
			throw err;
		}
	}
</script>

<StoreCreateForm onSubmit={handleSubmit} />
