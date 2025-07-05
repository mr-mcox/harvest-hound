<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { fn } from 'storybook/test';
	import StoreCreateForm from '../routes/stores/create/+page.svelte';

	const { Story } = defineMeta({
		title: 'Forms/StoreCreateForm',
		component: StoreCreateForm,
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

<!-- With pre-filled data -->
<Story
	name="Pre-filled"
	args={{
		// Note: The component doesn't support initial values directly,
		// so this would need to be enhanced in the actual component
	}}
/>

<!-- With validation error -->
<Story
	name="With Error"
	args={{
		// This would need error prop support in the component
	}}
/>

<!-- Infinite supply enabled -->
<Story
	name="Infinite Supply"
	args={{
		// This would need initial state support
	}}
/>

<!-- Loading state -->
<Story
	name="Loading"
	args={{
		// This would need loading prop support
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
