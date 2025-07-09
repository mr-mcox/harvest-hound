/**
 * Svelte store for WebSocket connection state and events.
 *
 * This store provides reactive WebSocket connection state and event handling
 * for Svelte components to subscribe to real-time updates.
 */

import { writable, derived } from 'svelte/store';
import { WebSocketService, ConnectionState, type WebSocketMessage } from './websocket-service';

/**
 * WebSocket store state interface
 */
export interface WebSocketStoreState {
	connectionState: ConnectionState;
	lastMessage: WebSocketMessage | null;
	error: string | null;
}

/**
 * WebSocket store class for managing reactive state
 */
export class WebSocketStore {
	private service: WebSocketService;
	private state = writable<WebSocketStoreState>({
		connectionState: ConnectionState.DISCONNECTED,
		lastMessage: null,
		error: null
	});

	constructor(url: string) {
		this.service = new WebSocketService(url);

		// Subscribe to service state changes
		this.service.on('connectionStateChange', (state: ConnectionState) => {
			this.updateState({ connectionState: state });
		});

		this.service.on('message', (message: WebSocketMessage) => {
			this.updateState({ lastMessage: message });
		});

		this.service.on('error', (error: string) => {
			this.updateState({ error });
		});
	}

	/**
	 * Get readable store for connection state
	 */
	get connectionState() {
		return derived(this.state, ($state) => $state.connectionState);
	}

	/**
	 * Get readable store for last received message
	 */
	get lastMessage() {
		return derived(this.state, ($state) => $state.lastMessage);
	}

	/**
	 * Get readable store for error state
	 */
	get error() {
		return derived(this.state, ($state) => $state.error);
	}

	/**
	 * Connect to WebSocket server
	 */
	connect(): void {
		this.service.connect();
	}

	/**
	 * Disconnect from WebSocket server
	 */
	disconnect(): void {
		this.service.disconnect();
	}

	/**
	 * Update store state
	 */
	private updateState(update: Partial<WebSocketStoreState>): void {
		this.state.update((currentState) => ({ ...currentState, ...update }));
	}
}

/**
 * Create WebSocket store instance
 */
export function createWebSocketStore(url: string): WebSocketStore {
	return new WebSocketStore(url);
}

/**
 * Default WebSocket store instance
 */
export const websocketStore = createWebSocketStore(`ws://localhost:8000/ws`);
