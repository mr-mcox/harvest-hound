import { describe, expect, it } from 'vitest';
import { validateStoreForm } from '$lib/validation';

// Test form validation logic directly
describe('Store Creation - Core Validation Logic', () => {
	it('validates form data correctly for valid input', () => {
		const validData = {
			name: 'Test Store',
			description: 'Test Description',
			infinite_supply: true
		};

		const result = validateStoreForm(validData);
		expect(result).toEqual({ valid: true });
	});

	it('returns error when name is empty', () => {
		const invalidData = {
			name: '',
			description: 'Test Description',
			infinite_supply: false
		};

		const result = validateStoreForm(invalidData);
		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('returns error when name is null', () => {
		const invalidData = {
			name: null,
			description: 'Test Description',
			infinite_supply: false
		};

		const result = validateStoreForm(invalidData);
		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('returns error when name is only whitespace', () => {
		const invalidData = {
			name: '   ',
			description: 'Test Description',
			infinite_supply: false
		};

		const result = validateStoreForm(invalidData);
		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('returns error when name is too long', () => {
		const longName = 'a'.repeat(101); // Over 100 characters
		const invalidData = {
			name: longName,
			description: 'Test Description',
			infinite_supply: false
		};

		const result = validateStoreForm(invalidData);
		expect(result).toEqual({ error: 'Store name must be 100 characters or less' });
	});

	it('allows empty description', () => {
		const validData = {
			name: 'Valid Store',
			description: '',
			infinite_supply: false
		};

		const result = validateStoreForm(validData);
		expect(result).toEqual({ valid: true });
	});

	it('allows undefined description', () => {
		const validData = {
			name: 'Valid Store',
			infinite_supply: true
		};

		const result = validateStoreForm(validData);
		expect(result).toEqual({ valid: true });
	});

	it('handles different infinite_supply values correctly', () => {
		const testCases = [
			{ infinite_supply: true },
			{ infinite_supply: false },
			{ infinite_supply: undefined }
		];

		testCases.forEach(({ infinite_supply }) => {
			const data = {
				name: 'Test Store',
				description: 'Test',
				infinite_supply
			};

			const result = validateStoreForm(data);
			expect(result).toEqual({ valid: true });
		});
	});
});
