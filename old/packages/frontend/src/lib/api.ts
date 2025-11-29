// API configuration and utilities

// Get API base URL from environment variable
// Always use localhost:8000 for browser-based API calls since the backend is exposed on host port 8000
export const API_BASE_URL = 'http://localhost:8000';

// Helper function to make API calls with proper base URL
export async function apiCall(endpoint: string, options?: RequestInit): Promise<Response> {
	const url = `${API_BASE_URL}${endpoint}`;
	return fetch(url, options);
}

// Helper function to make GET requests
export async function apiGet(endpoint: string): Promise<Response> {
	return apiCall(endpoint, { method: 'GET' });
}

// Helper function to make POST requests
export async function apiPost(endpoint: string, data?: unknown): Promise<Response> {
	return apiCall(endpoint, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: data ? JSON.stringify(data) : undefined
	});
}
