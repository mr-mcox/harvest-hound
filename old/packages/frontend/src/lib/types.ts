/**
 * Type definitions for Harvest Hound frontend
 *
 * Re-exports types from generated backend schemas plus additional frontend types
 */

// Re-export all generated types from backend
export * from './generated/api-types.js';

/**
 * Frontend-specific types (backend types are re-exported above)
 */

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
