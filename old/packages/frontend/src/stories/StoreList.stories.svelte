<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import StoreList from '../lib/components/StoreList.svelte';

	const mockStores = [
		{
			store_id: 'store-1',
			name: 'CSA Box',
			description: 'Weekly community supported agriculture box',
			infinite_supply: false,
			item_count: 5,
			created_at: '2024-01-01T10:00:00Z'
		},
		{
			store_id: 'store-2',
			name: 'Pantry',
			description: 'Long-term storage items',
			infinite_supply: true,
			item_count: 12,
			created_at: '2024-01-01T11:00:00Z'
		},
		{
			store_id: 'store-3',
			name: 'Freezer',
			description: 'Frozen ingredients',
			infinite_supply: false,
			item_count: 8,
			created_at: '2024-01-01T12:00:00Z'
		}
	];

	const { Story } = defineMeta({
		title: 'Lists/StoreList',
		component: StoreList,
		tags: ['autodocs'],
		argTypes: {
			stores: { control: 'object' },
			loading: { control: 'boolean' },
			error: { control: 'text' }
		},
		args: {
			stores: mockStores,
			loading: false,
			error: null
		}
	});
</script>

<!-- Default state with stores -->
<Story
	name="Default"
	args={{
		stores: mockStores,
		loading: false,
		error: null
	}}
/>

<!-- Empty state -->
<Story
	name="Empty"
	args={{
		stores: [],
		loading: false,
		error: null
	}}
/>

<!-- Loading state -->
<Story
	name="Loading"
	args={{
		stores: [],
		loading: true,
		error: null
	}}
/>

<!-- Error state -->
<Story
	name="Error"
	args={{
		stores: [],
		loading: false,
		error: 'Failed to load stores from the server'
	}}
/>

<!-- Single store -->
<Story
	name="Single Store"
	args={{
		stores: [mockStores[0]],
		loading: false,
		error: null
	}}
/>

<!-- Stores with no descriptions -->
<Story
	name="No Descriptions"
	args={{
		stores: [
			{
				store_id: 'store-1',
				name: 'CSA Box',
				description: undefined,
				infinite_supply: false,
				item_count: 5,
				created_at: '2024-01-01T10:00:00Z'
			},
			{
				store_id: 'store-2',
				name: 'Pantry',
				description: undefined,
				infinite_supply: true,
				item_count: 12,
				created_at: '2024-01-01T11:00:00Z'
			}
		],
		loading: false,
		error: null
	}}
/>

<!-- Stores with zero items -->
<Story
	name="Zero Items"
	args={{
		stores: [
			{
				store_id: 'store-1',
				name: 'New Store',
				description: 'Recently created store',
				infinite_supply: false,
				item_count: 0,
				created_at: '2024-01-01T10:00:00Z'
			}
		],
		loading: false,
		error: null
	}}
/>

<!-- Mobile view -->
<Story
	name="Mobile View"
	args={{
		stores: mockStores,
		loading: false,
		error: null
	}}
	parameters={{
		viewport: {
			defaultViewport: 'mobile1'
		}
	}}
/>
