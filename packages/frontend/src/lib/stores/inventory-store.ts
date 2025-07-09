/**
 * Centralized inventory store for managing inventory data with real-time WebSocket updates.
 * 
 * This store provides reactive state management for inventory data, automatically
 * updating when WebSocket events are received for inventory changes.
 */

import { writable, derived, get } from 'svelte/store';
import { apiGet } from '$lib/api';
import { websocketStore } from '$lib/websocket-store';
import type { InventoryItemView, StoreView } from '$lib/types';

/**
 * Inventory store state interface
 */
interface InventoryStoreState {
	stores: StoreView[];
	inventoryByStoreId: Record<string, InventoryItemView[]>;
	loading: boolean;
	error: string | null;
	lastUpdate: Date | null;
}

/**
 * Initial state
 */
const initialState: InventoryStoreState = {
	stores: [],
	inventoryByStoreId: {},
	loading: false,
	error: null,
	lastUpdate: null
};

/**
 * Core inventory store
 */
const inventoryState = writable<InventoryStoreState>(initialState);

/**
 * Real-time event handlers for WebSocket updates
 */
function handleInventoryItemAdded(data: {
	store_id: string;
	ingredient_id: string;
	quantity: number;
	unit: string;
	notes?: string;
	added_at: string;
}) {
	inventoryState.update(state => {
		// If we don't have inventory for this store loaded, don't update
		if (!state.inventoryByStoreId[data.store_id]) {
			return state;
		}

		// Create new inventory item from the event data
		// Note: We'd need ingredient name from the event or make additional API call
		// For now, we'll trigger a refresh of the store's inventory
		return {
			...state,
			lastUpdate: new Date()
		};
	});

	// For real-time updates, refresh the specific store's inventory
	// This ensures we get the full denormalized view with ingredient names
	const currentState = get(inventoryState);
	if (currentState.inventoryByStoreId[data.store_id]) {
		loadInventoryForStore(data.store_id);
	}
}

function handleStoreCreated(data: {
	store_id: string;
	name: string;
	description: string;
	infinite_supply: boolean;
	created_at: string;
}) {
	inventoryState.update(state => ({
		...state,
		stores: [
			...state.stores,
			{
				store_id: data.store_id,
				name: data.name,
				description: data.description,
				infinite_supply: data.infinite_supply,
				item_count: 0, // New store starts with 0 items
				created_at: data.created_at
			}
		],
		lastUpdate: new Date()
	}));
}

/**
 * Subscribe to WebSocket events for real-time updates
 */
function subscribeToWebSocketEvents(): () => void {
	// Subscribe to inventory-related events
	const unsubscribeMessage = websocketStore.lastMessage.subscribe((message) => {
		if (!message) return;

		switch (message.type) {
			case 'InventoryItemAdded':
				handleInventoryItemAdded(message.data as any);
				break;
			case 'StoreCreated':
				handleStoreCreated(message.data as any);
				break;
		}
	});

	return unsubscribeMessage;
}

/**
 * Load all stores from API
 */
async function loadStores() {
	inventoryState.update(state => ({ ...state, loading: true, error: null }));

	try {
		const response = await apiGet('/stores');
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const stores: StoreView[] = await response.json();
		
		inventoryState.update(state => ({
			...state,
			stores,
			loading: false,
			lastUpdate: new Date()
		}));
	} catch (error) {
		inventoryState.update(state => ({
			...state,
			loading: false,
			error: error instanceof Error ? error.message : 'Failed to load stores'
		}));
	}
}

/**
 * Load inventory for a specific store
 */
async function loadInventoryForStore(storeId: string) {
	inventoryState.update(state => ({ ...state, loading: true, error: null }));

	try {
		const response = await apiGet(`/stores/${storeId}/inventory`);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const inventory: InventoryItemView[] = await response.json();
		
		inventoryState.update(state => ({
			...state,
			inventoryByStoreId: {
				...state.inventoryByStoreId,
				[storeId]: inventory
			},
			loading: false,
			lastUpdate: new Date()
		}));
	} catch (error) {
		inventoryState.update(state => ({
			...state,
			loading: false,
			error: error instanceof Error ? error.message : 'Failed to load inventory'
		}));
	}
}

/**
 * Clear inventory data for a store (useful when navigating away)
 */
function clearInventoryForStore(storeId: string) {
	inventoryState.update(state => {
		const { [storeId]: _, ...remainingInventory } = state.inventoryByStoreId;
		return {
			...state,
			inventoryByStoreId: remainingInventory
		};
	});
}

/**
 * Exported store interface
 */
export const inventoryStore = {
	// Core state
	subscribe: inventoryState.subscribe,
	
	// Derived stores for specific data
	stores: derived(inventoryState, $state => $state.stores),
	loading: derived(inventoryState, $state => $state.loading),
	error: derived(inventoryState, $state => $state.error),
	lastUpdate: derived(inventoryState, $state => $state.lastUpdate),
	
	// Get inventory for specific store
	getInventoryForStore: (storeId: string) => 
		derived(inventoryState, $state => $state.inventoryByStoreId[storeId] || []),
	
	// Actions
	loadStores,
	loadInventoryForStore,
	clearInventoryForStore,
	subscribeToWebSocketEvents,
	
	// Reset store state
	reset: () => inventoryState.set(initialState)
};