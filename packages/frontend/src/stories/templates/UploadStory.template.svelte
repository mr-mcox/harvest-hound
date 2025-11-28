<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';

	interface UploadStoryOptions {
		argTypes?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
		args?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
	}

	// Base template for upload component stories
	export function createUploadStory(
		component: any, // eslint-disable-line @typescript-eslint/no-explicit-any
		title?: string,
		options: UploadStoryOptions = {}
	) {
		const { Story } = defineMeta({
			title: title || `Upload/${component.name}`,
			component,
			tags: ['autodocs'],
			argTypes: {
				loading: { control: 'boolean' },
				error: { control: 'text' },
				success: { control: 'text' },
				disabled: { control: 'boolean' },
				...options.argTypes
			},
			args: {
				loading: false,
				error: '',
				success: '',
				disabled: false,
				...options.args
			}
		});

		return { Story };
	}
</script>

<!-- Base upload story template -->
<div class="max-w-lg p-4">
	<slot />
</div>
