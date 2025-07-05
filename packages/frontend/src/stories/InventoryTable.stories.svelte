<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import InventoryTable from '../routes/stores/[id]/+page.svelte';
	import { mockData } from './templates/index.js';

	const { Story } = defineMeta({
		title: 'Tables/InventoryTable',
		component: InventoryTable,
		tags: ['autodocs'],
		argTypes: {
			inventory: { control: 'object' }
		},
		args: {
			inventory: []
		}
	});
</script>

<!-- Empty state -->
<Story
	name="Empty"
	args={{
		inventory: []
	}}
/>

<!-- With data -->
<Story
	name="With Data"
	args={{
		inventory: mockData.inventoryItems
	}}
/>

<!-- Single item -->
<Story
	name="Single Item"
	args={{
		inventory: [mockData.inventoryItems[0]]
	}}
/>

<!-- Large dataset -->
<Story
	name="Large Dataset"
	args={{
		inventory: [
			...mockData.inventoryItems,
			{
				id: 4,
				ingredient_name: 'Onions',
				quantity: 5,
				unit: 'whole',
				store_name: 'CSA Box',
				notes: 'Sweet onions'
			},
			{
				id: 5,
				ingredient_name: 'Potatoes',
				quantity: 3,
				unit: 'lbs',
				store_name: 'CSA Box',
				notes: 'Russet variety'
			},
			{
				id: 6,
				ingredient_name: 'Bell Peppers',
				quantity: 4,
				unit: 'whole',
				store_name: 'CSA Box',
				notes: 'Mixed colors'
			},
			{
				id: 7,
				ingredient_name: 'Spinach',
				quantity: 2,
				unit: 'bunches',
				store_name: 'CSA Box',
				notes: 'Fresh picked'
			},
			{
				id: 8,
				ingredient_name: 'Cucumbers',
				quantity: 6,
				unit: 'whole',
				store_name: 'CSA Box',
				notes: null
			},
			{
				id: 9,
				ingredient_name: 'Zucchini',
				quantity: 3,
				unit: 'whole',
				store_name: 'CSA Box',
				notes: 'Large size'
			},
			{
				id: 10,
				ingredient_name: 'Herbs',
				quantity: 1,
				unit: 'bunch',
				store_name: 'CSA Box',
				notes: 'Mixed herbs'
			}
		]
	}}
/>

<!-- With long ingredient names -->
<Story
	name="Long Names"
	args={{
		inventory: [
			{
				id: 1,
				ingredient_name: 'Organic Rainbow Carrots with Greens Attached',
				quantity: 2.5,
				unit: 'lbs',
				store_name: 'Premium CSA Box',
				notes: 'Heirloom variety from local farm'
			},
			{
				id: 2,
				ingredient_name: 'Baby Red Russian Kale',
				quantity: 1,
				unit: 'large bunch',
				store_name: 'Premium CSA Box',
				notes: 'Tender leaves, perfect for salads'
			},
			{
				id: 3,
				ingredient_name: 'Heritage Cherry Tomatoes on the Vine',
				quantity: 12,
				unit: 'whole clusters',
				store_name: 'Premium CSA Box',
				notes: 'Sweet and juicy, various colors'
			}
		]
	}}
/>

<!-- Mobile view -->
<Story
	name="Mobile View"
	args={{
		inventory: mockData.inventoryItems
	}}
	parameters={{
		viewport: {
			defaultViewport: 'mobile1'
		}
	}}
/>
