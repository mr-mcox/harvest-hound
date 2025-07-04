import { page } from '@vitest/browser/context';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import CreateStorePage from './+page.svelte';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('Store Creation Form', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('should call POST /stores with form data when submitted', async () => {
		// Arrange
		mockFetch.mockResolvedValueOnce(new Response(
			JSON.stringify({ store_id: 'test-id', name: 'Test Store' }),
			{ status: 201, headers: { 'content-type': 'application/json' } }
		));

		const submitHandler = vi.fn();
		render(CreateStorePage, { props: { onSubmit: submitHandler } });

		// Act
		const nameInput = page.getByLabelText('Store Name');
		const descriptionInput = page.getByLabelText('Description');
		const infiniteSupplyCheckbox = page.getByLabelText('Infinite Supply');
		const submitButton = page.getByRole('button', { name: 'Create Store' });

		await nameInput.fill('Test Store');
		await descriptionInput.fill('Test Description');
		await infiniteSupplyCheckbox.check();
		await submitButton.click();

		// Assert
		expect(submitHandler).toHaveBeenCalledWith({
			name: 'Test Store',
			description: 'Test Description',
			infinite_supply: true
		});
	});

	it('should show validation error for empty name field', async () => {
		// Arrange
		const submitHandler = vi.fn();
		render(CreateStorePage, { props: { onSubmit: submitHandler } });

		// Act
		const submitButton = page.getByRole('button', { name: 'Create Store' });
		await submitButton.click();

		// Assert
		const errorMessage = page.getByText('Store name is required');
		await expect.element(errorMessage).toBeInTheDocument();
		expect(submitHandler).not.toHaveBeenCalled();
	});
});
