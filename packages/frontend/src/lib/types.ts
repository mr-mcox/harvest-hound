/**
 * Shared type definitions that should match backend Pydantic models
 * TODO: Generate these automatically from backend schemas
 */

export interface InventoryItem {
	/** UUID of the store this item belongs to */
	store_id: string;
	
	/** UUID of the ingredient */
	ingredient_id: string;
	
	/** Quantity of the ingredient (decimal number) */
	quantity: number;
	
	/** Unit of measurement (should be validated against allowed units) */
	unit: string;
	
	/** Optional notes about this inventory item */
	notes?: string;
	
	/** ISO datetime string when item was added */
	added_at: string;
}

export interface InventoryItemWithIngredient extends InventoryItem {
	/** Name of the ingredient (from ingredient table join) */
	ingredient_name: string;
}

export interface Ingredient {
	/** UUID of the ingredient */
	ingredient_id: string;
	
	/** Canonical name of the ingredient */
	name: string;
	
	/** Default unit for this ingredient */
	default_unit: string;
	
	/** ISO datetime string when ingredient was created */
	created_at: string;
}

export interface Store {
	/** UUID of the store */
	store_id: string;
	
	/** Name of the store */
	name: string;
	
	/** Optional description */
	description?: string;
	
	/** Whether this store has infinite supply */
	infinite_supply: boolean;
	
	/** ISO datetime string when store was created */
	created_at: string;
}

// API Response types
export interface StoreListResponse {
	stores: Array<Store & { item_count: number }>;
}

export interface InventoryUploadResult {
	items_added: number;
	errors?: string[];
}