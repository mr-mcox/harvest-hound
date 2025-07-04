import { page } from '@vitest/browser/context';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import InventoryUploadPage from './+page.svelte';

describe('Inventory Upload Component UI Behavior', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('should call onSubmit handler with inventory text when form is submitted', async () => {
		// Arrange
		const submitHandler = vi.fn();
		render(InventoryUploadPage, { props: { onSubmit: submitHandler } });

		// Act
		const textArea = page.getByLabelText('Inventory Items');
		const submitButton = page.getByRole('button', { name: 'Upload Inventory' });

		await textArea.fill('2 lbs carrots\n1 bunch kale\n3 tomatoes');
		await submitButton.click();

		// Assert
		expect(submitHandler).toHaveBeenCalledWith({
			inventoryText: '2 lbs carrots\n1 bunch kale\n3 tomatoes'
		});
	});

	it('should show loading state while upload is in progress', async () => {
		// Arrange
		const submitHandler = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
		render(InventoryUploadPage, { props: { onSubmit: submitHandler } });

		// Act
		const textArea = page.getByLabelText('Inventory Items');
		const submitButton = page.getByRole('button', { name: 'Upload Inventory' });

		await textArea.fill('2 lbs carrots');
		await submitButton.click();

		// Assert - Button should show loading state
		const loadingButton = page.getByRole('button', { name: 'Uploading...' });
		await expect.element(loadingButton).toBeInTheDocument();

		// Button should be disabled during loading
		await expect.element(loadingButton).toBeDisabled();
	});

	it('should display success message with items count after successful upload', async () => {
		// Arrange
		const submitHandler = vi.fn().mockResolvedValue({ items_added: 3 });
		render(InventoryUploadPage, { props: { onSubmit: submitHandler } });

		// Act
		const textArea = page.getByLabelText('Inventory Items');
		const submitButton = page.getByRole('button', { name: 'Upload Inventory' });

		await textArea.fill('2 lbs carrots\n1 bunch kale\n3 tomatoes');
		await submitButton.click();

		// Wait for success message
		const successMessage = page.getByText('Successfully added 3 items to inventory');
		await expect.element(successMessage).toBeInTheDocument();
	});

	it('should display error message when upload fails with parse error', async () => {
		// Arrange
		const submitHandler = vi.fn().mockRejectedValue(new Error('Failed to parse: invalid format'));
		render(InventoryUploadPage, { props: { onSubmit: submitHandler } });

		// Act
		const textArea = page.getByLabelText('Inventory Items');
		const submitButton = page.getByRole('button', { name: 'Upload Inventory' });

		await textArea.fill('invalid inventory format');
		await submitButton.click();

		// Assert
		const errorMessage = page.getByText('Failed to parse: invalid format');
		await expect.element(errorMessage).toBeInTheDocument();
	});

	it('should clear previous messages when new upload is attempted', async () => {
		// Arrange
		const submitHandler = vi.fn()
			.mockRejectedValueOnce(new Error('First error'))
			.mockResolvedValueOnce({ items_added: 2 });

		render(InventoryUploadPage, { props: { onSubmit: submitHandler } });

		// Act - First upload fails
		const textArea = page.getByLabelText('Inventory Items');
		const submitButton = page.getByRole('button', { name: 'Upload Inventory' });

		await textArea.fill('invalid format');
		await submitButton.click();

		// Verify error shows
		const errorMessage = page.getByText('First error');
		await expect.element(errorMessage).toBeInTheDocument();

		// Act - Second upload succeeds
		await textArea.fill('2 lbs carrots\n1 bunch kale');
		await submitButton.click();

		// Assert - Error is cleared, success shows
		await expect.element(errorMessage).not.toBeInTheDocument();
		const successMessage = page.getByText('Successfully added 2 items to inventory');
		await expect.element(successMessage).toBeInTheDocument();
	});
});
