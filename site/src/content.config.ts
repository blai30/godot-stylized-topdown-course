import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';

// A lesson page states its number, its time estimate (an hour at most), what it teaches, and the lesson numbers it
// builds on.
const lesson = z.object({
	number: z.number().int().positive(),
	minutes: z.number().int().positive().max(60),
	learn: z.array(z.string()).min(1),
	prerequisites: z.array(z.number().int().positive()).default([]),
});

export const collections = {
	docs: defineCollection({
		loader: docsLoader(),
		schema: docsSchema({ extend: z.object({ lesson: lesson.optional() }) }),
	}),
	// Starlight always reads this collection; an empty en.json keeps the built-in strings and its build log quiet
	// (an upstream Starlight 0.42 and Astro 7.4 issue).
	i18n: defineCollection({ loader: i18nLoader(), schema: i18nSchema() }),
};
