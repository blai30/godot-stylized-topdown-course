import { existsSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { modules } from './src/data/syllabus';

// A module appears in the sidebar once its folder has lessons in it.
const published = modules.filter((module) => existsSync(`./src/content/docs/${module.directory}`));

// The site is a GitHub Pages project site, so it lives under its repository's name. Local builds serve from the root.
const base = process.env.SITE_BASE ?? '/';

export default defineConfig({
	site: process.env.SITE_URL ?? 'https://blai30.github.io',
	base,
	integrations: [
		starlight({
			title: 'Handmade Meadow',
			// The 404 page lives in src/pages/404.astro.
			disable404Route: true,
			description: 'Build a stylized top-down Godot game template by hand, from the first install to your own art library.',
			customCss: [
				'@fontsource-variable/fraunces/full.css',
				'@fontsource-variable/inter',
				'@fontsource-variable/jetbrains-mono',
				'./src/styles/theme.css',
			],
			// Long code lines wrap instead of scrolling, so phone readers see every line without a scroll bar to reach.
			expressiveCode: { defaultProps: { wrap: true } },
			components: {
				PageTitle: './src/components/overrides/PageTitle.astro',
				Search: './src/components/overrides/Search.astro',
				Sidebar: './src/components/overrides/Sidebar.astro',
			},
			sidebar: [
				{ label: 'Start here', items: ['start/how-this-course-works', 'start/syllabus'] },
				...published.map((module) => ({
					label: `Module ${module.number}: ${module.title}`,
					items: [{ autogenerate: { directory: module.directory } }],
				})),
				{ label: 'Reference', items: ['reference/glossary', 'reference/credits'] },
			],
		}),
	],
});
