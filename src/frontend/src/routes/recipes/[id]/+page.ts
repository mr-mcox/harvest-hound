import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ params, fetch }) => {
  const response = await fetch(`/api/recipes/${params.id}`);

  if (!response.ok) {
    throw new Error(`Failed to load recipe: ${response.status}`);
  }

  const recipe = await response.json();

  return {
    recipe,
  };
};
