import { describe, expect, it } from 'vitest';
import { validateStoreForm } from './validation.js';

describe('validateStoreForm', () => {
	it('should return valid: true for valid store data', () => {
		const result = validateStoreForm({
			name: 'Test Store',
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ valid: true });
	});

	it('should reject empty name', () => {
		const result = validateStoreForm({
			name: '',
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject whitespace-only name', () => {
		const result = validateStoreForm({
			name: '   ',
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject undefined name', () => {
		const result = validateStoreForm({
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject null name', () => {
		const result = validateStoreForm({
			name: null,
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ error: 'Store name is required' });
	});

	it('should reject name longer than 100 characters', () => {
		const longName = 'a'.repeat(101);
		const result = validateStoreForm({
			name: longName,
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ error: 'Store name must be 100 characters or less' });
	});

	it('should accept name with exactly 100 characters', () => {
		const exactName = 'a'.repeat(100);
		const result = validateStoreForm({
			name: exactName,
			description: 'A test store',
			infinite_supply: false
		});

		expect(result).toEqual({ valid: true });
	});

	it('should accept empty description', () => {
		const result = validateStoreForm({
			name: 'Test Store',
			description: '',
			infinite_supply: false
		});

		expect(result).toEqual({ valid: true });
	});

	it('should accept any infinite_supply value', () => {
		const resultTrue = validateStoreForm({
			name: 'Test Store',
			description: 'Test',
			infinite_supply: true
		});

		const resultFalse = validateStoreForm({
			name: 'Test Store',
			description: 'Test',
			infinite_supply: false
		});

		expect(resultTrue).toEqual({ valid: true });
		expect(resultFalse).toEqual({ valid: true });
	});
});
