<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { fn } from 'storybook/test';
	import InventoryUpload from '../routes/stores/[id]/upload/+page.svelte';

	const { Story } = defineMeta({
		title: 'Forms/InventoryUpload',
		component: InventoryUpload,
		tags: ['autodocs'],
		argTypes: {
			onSubmit: { action: 'submitted' }
		},
		args: {
			onSubmit: fn()
		}
	});
</script>

<!-- Default state -->
<Story name="Default" />

<!-- With sample text -->
<Story
	name="With Sample Text"
	args={{
		// Note: Component doesn't support initial text, would need enhancement
	}}
/>

<!-- Loading state - simulated with slow async function -->
<Story
	name="Loading State"
	args={{
		onSubmit: fn().mockImplementation(async () => {
			// Simulate loading
			await new Promise((resolve) => setTimeout(resolve, 2000));
			return { items_added: 3 };
		})
	}}
/>

<!-- Success state - simulated with successful response -->
<Story
	name="Success State"
	args={{
		onSubmit: fn().mockImplementation(async () => {
			return { items_added: 5 };
		})
	}}
/>

<!-- Error state - simulated with error -->
<Story
	name="Error State"
	args={{
		onSubmit: fn().mockImplementation(async () => {
			throw new Error('Failed to parse inventory: Invalid format');
		})
	}}
/>

<!-- Large text input -->
<Story
	name="Large Input"
	args={{
		// Would need initial text support
	}}
/>

<!-- Mobile view -->
<Story
	name="Mobile View"
	parameters={{
		viewport: {
			defaultViewport: 'mobile1'
		}
	}}
/>
