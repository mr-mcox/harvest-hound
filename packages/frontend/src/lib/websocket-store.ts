/**
 * Svelte store for WebSocket connection state and events.
 *
 * This store provides reactive WebSocket connection state and event handling
 * for Svelte components to subscribe to real-time updates.
 */

/* eslint-disable @typescript-eslint/no-unused-vars */

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
		throw new Error('TODO: implement in NEW BEHAVIOR task');
	}

	/**
	 * Disconnect from WebSocket server
	 */
	disconnect(): void {
		throw new Error('TODO: implement in NEW BEHAVIOR task');
	}

	/**
	 * Send message to WebSocket server
	 */
	send(_: WebSocketMessage): void {
		throw new Error('TODO: implement in NEW BEHAVIOR task');
	}

	/**
	 * Subscribe to specific event types
	 */
	on<T = unknown>(_: string, __: (data: T) => void): void {
		throw new Error('TODO: implement in NEW BEHAVIOR task');
	}

	/**
	 * Unsubscribe from specific event types
	 */
	off(_: string, __: (data: unknown) => void): void {
		throw new Error('TODO: implement in NEW BEHAVIOR task');
	}

	/**
	 * Update store state
	 */
	private updateState(_: Partial<WebSocketStoreState>): void {
		throw new Error('TODO: implement in NEW BEHAVIOR task');
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
