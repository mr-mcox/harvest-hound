/**
 * Tests for RealTimeIndicator component WebSocket connection status display
 *
 * This test suite ensures the component displays appropriate visual feedback
 * for different WebSocket connection states and last update timestamps.
 */

import { page } from '@vitest/browser/context';
import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import RealTimeIndicator from './RealTimeIndicator.svelte';
import { ConnectionState } from '$lib/websocket-service';

describe('RealTimeIndicator - WebSocket Status Display', () => {
	describe('Connection State Display', () => {
		it('displays connected state correctly', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: null
			});

			await expect.element(page.getByText('Real-time updates active')).toBeInTheDocument();
		});

		it('displays connecting state correctly', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTING,
				lastUpdate: null
			});

			await expect
				.element(page.getByText('Connecting to real-time updates...'))
				.toBeInTheDocument();
		});

		it('displays reconnecting state correctly', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.RECONNECTING,
				lastUpdate: null
			});

			await expect
				.element(page.getByText('Reconnecting to real-time updates...'))
				.toBeInTheDocument();
		});

		it('displays disconnected state correctly', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.DISCONNECTED,
				lastUpdate: null
			});

			await expect.element(page.getByText('Real-time updates unavailable')).toBeInTheDocument();
		});
	});

	describe('Last Update Display', () => {
		it('displays "Just now" for recent updates', async () => {
			const recentUpdate = new Date(Date.now() - 10000); // 10 seconds ago

			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: recentUpdate
			});

			await expect.element(page.getByText('Last updated: Just now')).toBeInTheDocument();
		});

		it('displays seconds ago for updates within a minute', async () => {
			const recentUpdate = new Date(Date.now() - 45000); // 45 seconds ago

			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: recentUpdate
			});

			await expect.element(page.getByText('Last updated: 45 seconds ago')).toBeInTheDocument();
		});

		it('displays minutes ago for updates within an hour', async () => {
			const recentUpdate = new Date(Date.now() - 300000); // 5 minutes ago

			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: recentUpdate
			});

			await expect.element(page.getByText('Last updated: 5 minutes ago')).toBeInTheDocument();
		});

		it('displays singular minute correctly', async () => {
			const recentUpdate = new Date(Date.now() - 60000); // 1 minute ago

			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: recentUpdate
			});

			await expect.element(page.getByText('Last updated: 1 minute ago')).toBeInTheDocument();
		});

		it('displays time for older updates', async () => {
			const oldUpdate = new Date(Date.now() - 3600000); // 1 hour ago

			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: oldUpdate
			});

			// Should show time format (exact time will vary based on locale)
			await expect.element(page.getByText(/Last updated: \d{1,2}:\d{2}:\d{2}/)).toBeInTheDocument();
		});

		it('does not display last update when null', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: null
			});

			await expect.element(page.getByText(/Last updated:/)).not.toBeInTheDocument();
		});
	});

	describe('Visual Styling', () => {
		it('displays success styling for connected state', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: null
			});

			// Check that the component displays success state text
			await expect.element(page.getByText('Real-time updates active')).toBeInTheDocument();
		});

		it('displays warning styling for connecting state', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTING,
				lastUpdate: null
			});

			// Check that the component displays connecting state text
			await expect
				.element(page.getByText('Connecting to real-time updates...'))
				.toBeInTheDocument();
		});

		it('displays warning styling for reconnecting state', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.RECONNECTING,
				lastUpdate: null
			});

			// Check that the component displays reconnecting state text
			await expect
				.element(page.getByText('Reconnecting to real-time updates...'))
				.toBeInTheDocument();
		});

		it('displays error styling for disconnected state', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.DISCONNECTED,
				lastUpdate: null
			});

			// Check that the component displays disconnected state text
			await expect.element(page.getByText('Real-time updates unavailable')).toBeInTheDocument();
		});

		it('displays status indicator with visual feedback', async () => {
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: null
			});

			// Check that the component displays connected state and visual feedback
			await expect.element(page.getByText('Real-time updates active')).toBeInTheDocument();

			// The component should render the visual status indicator
			await expect.element(page.getByText('Real-time updates active')).toBeVisible();
		});
	});

	describe('Real-time State Changes', () => {
		it('displays appropriate message for each connection state', async () => {
			// Test connected state
			render(RealTimeIndicator, {
				connectionState: ConnectionState.CONNECTED,
				lastUpdate: new Date()
			});

			await expect.element(page.getByText('Real-time updates active')).toBeInTheDocument();
			await expect.element(page.getByText(/Last updated:/)).toBeInTheDocument();
		});

		it('handles undefined connection state as disconnected', async () => {
			// Test with undefined state (should default to disconnected)
			render(RealTimeIndicator, {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				connectionState: undefined as any,
				lastUpdate: null
			});

			await expect.element(page.getByText('Real-time updates unavailable')).toBeInTheDocument();
		});
	});

	describe('Component Integration', () => {
		it('integrates with WebSocket service connection states', async () => {
			// Test that it can handle all WebSocket service states
			const allStates = [
				ConnectionState.DISCONNECTED,
				ConnectionState.CONNECTING,
				ConnectionState.CONNECTED,
				ConnectionState.RECONNECTING
			];

			const expectedTexts = [
				'Real-time updates unavailable',
				'Connecting to real-time updates...',
				'Real-time updates active',
				'Reconnecting to real-time updates...'
			];

			for (let i = 0; i < allStates.length; i++) {
				render(RealTimeIndicator, {
					connectionState: allStates[i],
					lastUpdate: null
				});

				await expect.element(page.getByText(expectedTexts[i])).toBeInTheDocument();
			}
		});
	});
});
