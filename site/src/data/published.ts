import { getCollection } from 'astro:content';

// The ids of the pages that exist, so unpublished lessons can be listed without links.
export async function publishedIds(): Promise<Set<string>> {
	return new Set((await getCollection('docs')).map(({ id }) => id));
}
