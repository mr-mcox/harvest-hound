import { test, expect } from '@playwright/test';

/**
 * Multi-tab real-time synchronization E2E tests
 *
 * These tests verify that the application works correctly across multiple
 * browser tabs and that data changes persist and are visible across sessions.
 */

test.describe('Multi-tab Real-time Synchronization', () => {
	test('multi-tab updates sync across browser sessions', async ({ browser }) => {
		// Create two browser contexts (simulating two browser tabs)
		const context1 = await browser.newContext();
		const context2 = await browser.newContext();

		const page1 = await context1.newPage();
		const page2 = await context2.newPage();

		try {
			// Navigate both tabs to the stores page
			await page1.goto('/stores');
			await page2.goto('/stores');

			// Wait for pages to load
			await page1.waitForSelector('[data-testid="realtime-indicator"]');
			await page2.waitForSelector('[data-testid="realtime-indicator"]');

			// Verify both tabs show the same initial state
			const initialStoresCount1 = await page1.locator('[data-testid="store-item"]').count();
			const initialStoresCount2 = await page2.locator('[data-testid="store-item"]').count();

			console.log('Initial store count in tab 1:', initialStoresCount1);
			console.log('Initial store count in tab 2:', initialStoresCount2);

			expect(initialStoresCount1).toBe(initialStoresCount2);

			// Navigate to create store page in tab 1
			await page1.click('[data-testid="create-store-button"]');
			await page1.waitForURL('/stores/create');

			// Verify form is loaded
			await page1.waitForSelector('[data-testid="store-form"]');

			// Fill out and submit the form with unique name
			const uniqueStoreName = `Multi-tab Test Store ${Date.now()}`;
			await page1.fill('[data-testid="store-name-input"]', uniqueStoreName);
			await page1.fill(
				'[data-testid="store-description-input"]',
				'Testing multi-tab functionality'
			);
			await page1.click('[data-testid="submit-store-button"]');

			// Wait for navigation back to stores list
			await page1.waitForURL('/stores');
			await page1.waitForSelector('[data-testid="store-item"]');

			// Verify new store appears in tab 1
			await expect(page1.locator('[data-testid="store-item"]')).toHaveCount(
				initialStoresCount1 + 1
			);
			await expect(page1.locator(`text=${uniqueStoreName}`)).toBeVisible();

			// Refresh tab 2 and verify the store appears there too
			await page2.reload();
			await page2.waitForSelector('[data-testid="store-item"]');

			// Verify new store appears in tab 2
			await expect(page2.locator('[data-testid="store-item"]')).toHaveCount(
				initialStoresCount2 + 1
			);
			await expect(page2.locator(`text=${uniqueStoreName}`)).toBeVisible();
		} finally {
			// Clean up contexts
			await context1.close();
			await context2.close();
		}
	});
});
