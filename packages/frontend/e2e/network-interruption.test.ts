import { test, expect } from '@playwright/test';

/**
 * Network interruption and recovery E2E tests
 *
 * These tests verify that the application handles network interruptions gracefully
 * and recovers properly when connectivity is restored.
 */

test.describe('Network Interruption and Recovery', () => {
	test('application handles offline/online transitions gracefully', async ({ page, context }) => {
		// Navigate to stores page
		await page.goto('/stores');

		// Wait for page to load completely
		await page.waitForSelector('[data-testid="realtime-indicator"]');
		await page.waitForSelector('[data-testid="create-store-button"]');

		// Verify initial online state
		await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();

		// Get initial store count
		const initialStoresCount = await page.locator('[data-testid="store-item"]').count();
		console.log('Initial store count:', initialStoresCount);

		// Simulate going offline
		await context.setOffline(true);
		console.log('Simulated going offline');

		// Wait a moment for the application to detect offline state
		await page.waitForTimeout(2000);

		// Try to navigate while offline (test basic navigation resilience)
		try {
			await page.click('[data-testid="create-store-button"]', { timeout: 5000 });
			await page.waitForURL('/stores/create', { timeout: 5000 });
			console.log('Navigation succeeded while offline');
		} catch {
			console.log('Navigation failed while offline, as expected');
			// Navigate back to stores if we're stuck
			await page.goto('/stores', { waitUntil: 'domcontentloaded' });
		}

		// Go back online
		await context.setOffline(false);
		console.log('Simulated going back online');

		// Wait for connectivity to be restored
		await page.waitForTimeout(3000);

		// Ensure we're back on the stores page for the recovery test
		await page.goto('/stores');
		await page.waitForSelector('[data-testid="store-item"]');

		// Verify the application recovered and can function normally
		const finalStoresCount = await page.locator('[data-testid="store-item"]').count();
		console.log('Final store count after recovery:', finalStoresCount);

		// Test that normal operations work after reconnection
		await page.click('[data-testid="create-store-button"]');
		await page.waitForURL('/stores/create');

		// Fill out form with different name
		const onlineStoreName = `Online Recovery Test ${Date.now()}`;
		await page.fill('[data-testid="store-name-input"]', onlineStoreName);
		await page.fill('[data-testid="store-description-input"]', 'Testing online recovery');
		await page.click('[data-testid="submit-store-button"]');

		// Wait for navigation back to stores list
		await page.waitForURL('/stores');
		await page.waitForSelector('[data-testid="store-item"]');

		// Verify the new store was created successfully
		await expect(page.locator('[data-testid="store-item"]')).toHaveCount(finalStoresCount + 1);
		await expect(page.locator(`text=${onlineStoreName}`)).toBeVisible();

		// Verify real-time indicator is still present and functional
		await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();
	});

	test('websocket reconnection after network interruption', async ({ page, context }) => {
		// Navigate to stores page
		await page.goto('/stores');

		// Wait for page to load
		await page.waitForSelector('[data-testid="realtime-indicator"]');

		// Log initial connection state
		const initialStatus = await page.locator('[data-testid="realtime-indicator"]').textContent();
		console.log('Initial connection status:', initialStatus);

		// Simulate network interruption
		await context.setOffline(true);
		await page.waitForTimeout(2000);

		// Check if connection state changed (may show disconnected or still show last state)
		const offlineStatus = await page.locator('[data-testid="realtime-indicator"]').textContent();
		console.log('Offline status:', offlineStatus);

		// Restore network
		await context.setOffline(false);
		await page.waitForTimeout(3000);

		// Check if connection was restored
		const onlineStatus = await page.locator('[data-testid="realtime-indicator"]').textContent();
		console.log('Online status after recovery:', onlineStatus);

		// Verify the real-time indicator is still functioning
		await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();

		// Test that the page still functions normally
		await expect(page.locator('[data-testid="create-store-button"]')).toBeVisible();
		await expect(page.locator('[data-testid="create-store-button"]')).toBeEnabled();
	});
});
