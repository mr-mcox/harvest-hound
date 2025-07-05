<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';

	interface FormStoryOptions {
		argTypes?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
		args?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
	}

	// Base template for form component stories
	export function createFormStory(component: any, title?: string, options: FormStoryOptions = {}) {
		// eslint-disable-line @typescript-eslint/no-explicit-any
		const { Story } = defineMeta({
			title: title || `Forms/${component.name}`,
			component,
			tags: ['autodocs'],
			argTypes: {
				disabled: { control: 'boolean' },
				loading: { control: 'boolean' },
				error: { control: 'text' },
				...options.argTypes
			},
			args: {
				disabled: false,
				loading: false,
				error: '',
				...options.args
			}
		});

		return { Story };
	}
</script>

<!-- Base form story template - not used directly but imported by other stories -->
<div class="max-w-md p-4">
	<slot />
</div>
