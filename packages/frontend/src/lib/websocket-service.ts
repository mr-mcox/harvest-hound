/**
 * WebSocket Service for handling real-time communication with the backend.
 *
 * This service manages WebSocket connection lifecycle including connection,
 * disconnection, and reconnection logic for real-time updates.
 */

import type { WebSocketMessage as GeneratedWebSocketMessage } from './generated/api-types';

/**
 * WebSocket connection states
 */
export enum ConnectionState {
	DISCONNECTED = 'disconnected',
	CONNECTING = 'connecting',
	CONNECTED = 'connected',
	RECONNECTING = 'reconnecting'
}

/**
 * WebSocket message interface - imported from generated backend types
 */
export type WebSocketMessage = GeneratedWebSocketMessage;

/**
 * Event handler callback type
 */
export type EventHandler<T = unknown> = (data: T) => void;

/**
 * WebSocket service class for managing connection lifecycle
 */
export class WebSocketService {
	private ws: WebSocket | null = null;
	private connectionState: ConnectionState = ConnectionState.DISCONNECTED;
	private eventHandlers: Map<string, EventHandler[]> = new Map();
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private isExplicitlyDisconnected = false;
	private reconnectTimeoutId: number | null = null;

	constructor(private url: string) {}

	/**
	 * Establish WebSocket connection
	 */
	connect(): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			return; // Already connected
		}

		this.isExplicitlyDisconnected = false;
		// Only set to CONNECTING if we're not already in RECONNECTING state
		if (this.connectionState !== ConnectionState.RECONNECTING) {
			this.connectionState = ConnectionState.CONNECTING;
			// Emit connection state change
			const handlers = this.eventHandlers.get('connectionStateChange');
			if (handlers) {
				handlers.forEach((handler) => handler(this.connectionState));
			}
		}
		this.ws = new WebSocket(this.url);

		this.ws.addEventListener('open', this.handleOpen.bind(this));
		this.ws.addEventListener('message', this.handleMessage.bind(this));
		this.ws.addEventListener('close', this.handleClose.bind(this));
		this.ws.addEventListener('error', this.handleError.bind(this));
	}

	/**
	 * Close WebSocket connection
	 */
	disconnect(): void {
		this.isExplicitlyDisconnected = true;
		this.connectionState = ConnectionState.DISCONNECTED;

		// Emit connection state change
		const handlers = this.eventHandlers.get('connectionStateChange');
		if (handlers) {
			handlers.forEach((handler) => handler(this.connectionState));
		}

		// Clear any pending reconnection
		if (this.reconnectTimeoutId !== null) {
			clearTimeout(this.reconnectTimeoutId);
			this.reconnectTimeoutId = null;
		}

		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
	}

	/**
	 * Send message to WebSocket server
	 */
	send(message: WebSocketMessage): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(message));
		}
	}

	/**
	 * Subscribe to WebSocket events
	 */
	on<T = unknown>(eventType: string, handler: EventHandler<T>): void {
		if (!this.eventHandlers.has(eventType)) {
			this.eventHandlers.set(eventType, []);
		}
		this.eventHandlers.get(eventType)?.push(handler as EventHandler);
	}

	/**
	 * Unsubscribe from WebSocket events
	 */
	off(eventType: string, handler: EventHandler): void {
		const handlers = this.eventHandlers.get(eventType);
		if (handlers) {
			const index = handlers.indexOf(handler);
			if (index > -1) {
				handlers.splice(index, 1);
			}
		}
	}

	/**
	 * Get current connection state
	 */
	getConnectionState(): ConnectionState {
		return this.connectionState;
	}

	/**
	 * Handle incoming WebSocket messages
	 */
	private handleMessage(event: MessageEvent): void {
		try {
			const message: WebSocketMessage = JSON.parse(event.data);

			// Emit generic message event for store
			const messageHandlers = this.eventHandlers.get('message');
			if (messageHandlers) {
				messageHandlers.forEach((handler) => handler(message));
			}

			// Emit specific event type handlers
			const typeHandlers = this.eventHandlers.get(message.type);
			if (typeHandlers) {
				typeHandlers.forEach((handler) => handler(message.data));
			}
		} catch (error) {
			console.error('Error parsing WebSocket message:', error);

			// Emit error event
			const errorHandlers = this.eventHandlers.get('error');
			if (errorHandlers) {
				errorHandlers.forEach((handler) => handler(`Error parsing message: ${error}`));
			}
		}
	}

	/**
	 * Handle WebSocket connection open
	 */
	private handleOpen(): void {
		this.connectionState = ConnectionState.CONNECTED;
		this.reconnectAttempts = 0;

		// Emit connection state change
		const handlers = this.eventHandlers.get('connectionStateChange');
		if (handlers) {
			handlers.forEach((handler) => handler(this.connectionState));
		}
	}

	/**
	 * Handle WebSocket connection close
	 */
	private handleClose(): void {
		this.connectionState = ConnectionState.DISCONNECTED;
		this.ws = null;

		// Emit connection state change
		const handlers = this.eventHandlers.get('connectionStateChange');
		if (handlers) {
			handlers.forEach((handler) => handler(this.connectionState));
		}

		// Only attempt to reconnect if not explicitly disconnected and no reconnection in progress
		if (
			!this.isExplicitlyDisconnected &&
			this.reconnectAttempts < this.maxReconnectAttempts &&
			this.reconnectTimeoutId === null
		) {
			this.attemptReconnect();
		}
	}

	/**
	 * Handle WebSocket connection error
	 */
	private handleError(error: Event): void {
		console.error('WebSocket error:', error);

		// Emit error event
		const handlers = this.eventHandlers.get('error');
		if (handlers) {
			handlers.forEach((handler) => handler(`WebSocket error: ${error}`));
		}
	}

	/**
	 * Attempt to reconnect with exponential backoff
	 */
	private attemptReconnect(): void {
		if (this.isExplicitlyDisconnected || this.reconnectAttempts >= this.maxReconnectAttempts) {
			return;
		}

		this.reconnectAttempts++;

		const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
		this.reconnectTimeoutId = setTimeout(() => {
			this.reconnectTimeoutId = null;
			if (!this.isExplicitlyDisconnected) {
				this.connectionState = ConnectionState.RECONNECTING;
				// Emit connection state change
				const handlers = this.eventHandlers.get('connectionStateChange');
				if (handlers) {
					handlers.forEach((handler) => handler(this.connectionState));
				}
				this.connect();
			}
		}, delay) as unknown as number;
	}
}
