<!--
  Real-time status indicator component
  
  Shows WebSocket connection status and last update timestamp to provide
  visual feedback about real-time functionality.
-->

<script lang="ts">
	import { ConnectionState } from '$lib/websocket-service';

	export let connectionState: ConnectionState = ConnectionState.DISCONNECTED;
	export let lastUpdate: Date | null = null;

	$: statusClass = getStatusClass(connectionState);
	$: statusText = getStatusText(connectionState);
	$: formattedLastUpdate = lastUpdate ? formatLastUpdate(lastUpdate) : null;

	function getStatusClass(state: ConnectionState): string {
		switch (state) {
			case ConnectionState.CONNECTED:
				return 'variant-filled-success';
			case ConnectionState.CONNECTING:
			case ConnectionState.RECONNECTING:
				return 'variant-filled-warning';
			case ConnectionState.DISCONNECTED:
			default:
				return 'variant-filled-error';
		}
	}

	function getStatusText(state: ConnectionState): string {
		switch (state) {
			case ConnectionState.CONNECTED:
				return 'Connected';
			case ConnectionState.CONNECTING:
				return 'Connecting...';
			case ConnectionState.RECONNECTING:
				return 'Reconnecting...';
			case ConnectionState.DISCONNECTED:
			default:
				return 'Disconnected';
		}
	}

	function formatLastUpdate(date: Date): string {
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffSeconds = Math.floor(diffMs / 1000);
		const diffMinutes = Math.floor(diffSeconds / 60);

		if (diffSeconds < 30) {
			return 'Just now';
		} else if (diffSeconds < 60) {
			return `${diffSeconds} seconds ago`;
		} else if (diffMinutes < 60) {
			return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
		} else {
			return date.toLocaleTimeString();
		}
	}
</script>

<div class="mb-4" data-testid="realtime-indicator">
	<div class="chip {statusClass}">
		<!-- Connection status indicator -->
		<div class="flex items-center gap-2">
			<div class="h-2 w-2 rounded-full bg-current opacity-75"></div>
			<span class="text-sm font-medium">{statusText}</span>
		</div>
	</div>

	{#if formattedLastUpdate}
		<div class="text-surface-500 mt-1 text-xs" data-testid="last-update">
			Last updated: {formattedLastUpdate}
		</div>
	{/if}
</div>

<style>
	.chip {
		display: inline-flex;
		align-items: center;
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.875rem;
		font-weight: 500;
	}
</style>
