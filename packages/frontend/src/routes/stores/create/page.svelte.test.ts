import { page } from '@vitest/browser/context';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import CreateStorePage from './+page.svelte';

describe('Store Creation Form UI Behavior', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('should call onSubmit handler with form data when valid form is submitted', async () => {
		// Arrange
		const submitHandler = vi.fn();
		render(CreateStorePage, { props: { onSubmit: submitHandler } });

		// Act - Fill out valid form
		const nameInput = page.getByLabelText('Store Name');
		const descriptionInput = page.getByLabelText('Description');
		const infiniteSupplyCheckbox = page.getByLabelText('Infinite Supply');
		const submitButton = page.getByRole('button', { name: 'Create Store' });

		await nameInput.fill('Test Store');
		await descriptionInput.fill('Test Description');
		await infiniteSupplyCheckbox.click();
		await submitButton.click();

		// Assert - UI calls handler with correct data
		expect(submitHandler).toHaveBeenCalledWith({
			name: 'Test Store',
			description: 'Test Description',
			infinite_supply: true
		});
	});

	it('should display validation error in UI when form submission fails validation', async () => {
		// Arrange
		const submitHandler = vi.fn();
		render(CreateStorePage, { props: { onSubmit: submitHandler } });

		// Act - Submit form with invalid data (empty name)
		const submitButton = page.getByRole('button', { name: 'Create Store' });
		await submitButton.click();

		// Assert - UI displays error message and doesn't call handler
		const errorMessage = page.getByText('Store name is required');
		await expect.element(errorMessage).toBeInTheDocument();
		expect(submitHandler).not.toHaveBeenCalled();
	});

	it('should clear error message when valid form is submitted after error', async () => {
		// Arrange
		const submitHandler = vi.fn();
		render(CreateStorePage, { props: { onSubmit: submitHandler } });

		// Act - First submit invalid form to show error
		const submitButton = page.getByRole('button', { name: 'Create Store' });
		await submitButton.click();

		// Verify error is shown
		const errorMessage = page.getByText('Store name is required');
		await expect.element(errorMessage).toBeInTheDocument();

		// Then fix the form and submit again
		const nameInput = page.getByLabelText('Store Name');
		await nameInput.fill('Valid Store Name');
		await submitButton.click();

		// Assert - Error is cleared and handler is called
		await expect.element(errorMessage).not.toBeInTheDocument();
		expect(submitHandler).toHaveBeenCalledWith({
			name: 'Valid Store Name',
			description: '',
			infinite_supply: false
		});
	});
});
