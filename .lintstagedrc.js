export default {
	// Frontend TypeScript/JavaScript/Svelte files
	'packages/frontend/src/**/*.{ts,js,svelte}': [
		'cd packages/frontend && pnpm exec eslint --fix',
		'cd packages/frontend && pnpm exec prettier --write'
	],
	
	// Frontend Svelte files (additional type checking)
	'packages/frontend/src/**/*.svelte': [
		'cd packages/frontend && pnpm exec svelte-check --tsconfig ./tsconfig.json'
	],
	
	// Backend Python files
	'packages/backend/**/*.py': [
		'cd packages/backend && uv run ruff check --fix',
		'cd packages/backend && uv run ruff format'
	]
};