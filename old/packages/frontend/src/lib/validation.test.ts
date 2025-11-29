import { describe, expect, it } from 'vitest';
import { validateStoreForm, type StoreFormData } from './validation.js';

describe('validateStoreForm', () => {
	it('should return valid: true for valid store data', () => {
		const data: StoreFormData = {
			name: 'Test Store',
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ valid: true });
	});

	it('should reject empty name', () => {
		const data: StoreFormData = {
			name: '',
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject whitespace-only name', () => {
		const data: StoreFormData = {
			name: '   ',
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject undefined name', () => {
		const data: StoreFormData = {
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject null name', () => {
		const data: StoreFormData = {
			name: null,
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject name longer than 100 characters', () => {
		const longName = 'a'.repeat(101);
		const data: StoreFormData = {
			name: longName,
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ error: 'Store name must be 100 characters or less' });
	});

	it('should accept name with exactly 100 characters', () => {
		const exactName = 'a'.repeat(100);
		const data: StoreFormData = {
			name: exactName,
			description: 'A test store',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ valid: true });
	});

	it('should accept empty description', () => {
		const data: StoreFormData = {
			name: 'Test Store',
			description: '',
			infinite_supply: false
		};
		const result = validateStoreForm(data);

		expect(result).toEqual({ valid: true });
	});

	it('should accept any infinite_supply value', () => {
		const dataTrue: StoreFormData = {
			name: 'Test Store',
			description: 'Test',
			infinite_supply: true
		};
		const dataFalse: StoreFormData = {
			name: 'Test Store',
			description: 'Test',
			infinite_supply: false
		};

		const resultTrue = validateStoreForm(dataTrue);
		const resultFalse = validateStoreForm(dataFalse);

		expect(resultTrue).toEqual({ valid: true });
		expect(resultFalse).toEqual({ valid: true });
	});
});
