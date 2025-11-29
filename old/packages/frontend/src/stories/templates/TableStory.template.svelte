<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';

	interface TableStoryOptions {
		argTypes?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
		args?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
		mockData?: any[]; // eslint-disable-line @typescript-eslint/no-explicit-any
	}

	// Base template for table component stories
	export function createTableStory(
		component: any, // eslint-disable-line @typescript-eslint/no-explicit-any
		title?: string,
		options: TableStoryOptions = {}
	) {
		const { Story } = defineMeta({
			title: title || `Tables/${component.name}`,
			component,
			tags: ['autodocs'],
			argTypes: {
				loading: { control: 'boolean' },
				empty: { control: 'boolean' },
				data: { control: 'object' },
				...options.argTypes
			},
			args: {
				loading: false,
				empty: false,
				data: options.mockData || [],
				...options.args
			}
		});

		return { Story };
	}
</script>

<!-- Base table story template -->
<div class="p-4">
	<slot />
</div>
