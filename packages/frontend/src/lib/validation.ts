/**
 * Store form data input type
 */
export interface StoreFormData {
	name?: string | null;
	description?: string;
	infinite_supply?: boolean;
}

/**
 * Validation result types
 */
export type ValidationResult = { valid: true } | { error: string };

/**
 * Validates store form data
 */
export function validateStoreForm(data: StoreFormData): ValidationResult {
	if (!data.name?.trim()) {
		return { error: 'Store name is required' };
	}

	if (data.name.trim().length > 100) {
		return { error: 'Store name must be 100 characters or less' };
	}

	return { valid: true };
}
