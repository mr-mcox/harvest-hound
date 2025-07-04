/**
 * Validates store form data
 * @param {Object} data - Form data to validate
 * @param {string} data.name - Store name
 * @param {string} data.description - Store description
 * @param {boolean} data.infinite_supply - Infinite supply flag
 * @returns {Object} Validation result with either { valid: true } or { error: string }
 */
export function validateStoreForm(data) {
	if (!data.name?.trim()) {
		return { error: 'Store name is required' };
	}

	if (data.name.trim().length > 100) {
		return { error: 'Store name must be 100 characters or less' };
	}

	return { valid: true };
}
