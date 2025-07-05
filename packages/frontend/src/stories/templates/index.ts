// Story template utilities
export { createFormStory } from './FormStory.template.svelte';
export { createTableStory } from './TableStory.template.svelte';
export { createUploadStory } from './UploadStory.template.svelte';

// Common mock data generators
export const mockData = {
	inventoryItems: [
		{ id: 1, ingredient_name: 'Carrots', quantity: 2, unit: 'lbs', store_name: 'CSA Box' },
		{ id: 2, ingredient_name: 'Kale', quantity: 1, unit: 'bunch', store_name: 'CSA Box' },
		{ id: 3, ingredient_name: 'Tomatoes', quantity: 3, unit: 'whole', store_name: 'CSA Box' }
	],

	stores: [
		{ id: 1, name: 'CSA Box', description: 'Weekly vegetable delivery', item_count: 12 },
		{ id: 2, name: 'Pantry', description: 'Dry goods and staples', item_count: 25 },
		{ id: 3, name: 'Freezer', description: 'Frozen ingredients', item_count: 8 }
	]
};

// Common story decorators
export const decorators = {
	withSkeletonTheme: (story: () => string) => `
    <div data-theme="cerberus" class="p-4">
      ${story()}
    </div>
  `,

	withMaxWidth: (story: () => string) => `
    <div class="max-w-2xl mx-auto p-4">
      ${story()}
    </div>
  `
};
