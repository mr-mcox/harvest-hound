export default {
	'**/*.{ts,js,svelte}': ['eslint --fix', 'prettier --write'],
	'**/*.svelte': ['svelte-check --tsconfig ./tsconfig.json', 'prettier --write']
};
