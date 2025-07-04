/**
 * Type definitions for Harvest Hound frontend
 *
 * Re-exports types from generated backend schemas plus additional frontend types
 */

// Re-export all generated types from backend
export * from './generated/api-types.js';

// Import specific types for extending
import type { InventoryItem } from './generated/api-types.js';

/**
 * Frontend-specific types that extend backend types
 */

/** InventoryItem with ingredient name joined from ingredient table */
export interface InventoryItemWithIngredient extends InventoryItem {
	/** Name of the ingredient (from ingredient table join) */
	ingredient_name: string;
}

/** API Response types for frontend operations */
export interface StoreListResponse {
	stores: Array<{
		store_id: string;
		name: string;
		description?: string;
		infinite_supply: boolean;
		created_at: string;
		item_count: number;
	}>;
}

export interface InventoryUploadResult {
	items_added: number;
	errors?: string[];
}
