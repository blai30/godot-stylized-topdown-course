// Runs axe-core on every page of the built site in a real browser, at a desktop and a phone width, and in the light and dark themes.
// Usage: node check-accessibility.mjs <dist folder> [base path]. Needs `npm install` in tools/verification and an installed
// Chromium (`npx playwright-core install chromium`), or set CHROME to a browser executable.
import { createServer } from 'node:http';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join, extname, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const dist = process.argv[2];
const base = (process.argv[3] ?? '').replace(/\/$/, '');
const axeSource = readFileSync(createRequire(import.meta.url).resolve('axe-core/axe.min.js'), 'utf8');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.json': 'application/json', '.woff2': 'font/woff2', '.xml': 'application/xml' };

const pages = [];
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).forEach((entry) => {
	const path = join(dir, entry.name);
	if (entry.isDirectory()) walk(path);
	else if (entry.name.endsWith('.html')) pages.push(path.slice(dist.length).replace(/index\.html$/, '').replace(/\\/g, '/'));
});
walk(dist);

const server = createServer((request, response) => {
	let path = decodeURIComponent(new URL(request.url, 'http://x').pathname);
	if (base && path.startsWith(base)) path = path.slice(base.length) || '/';
	let file = join(dist, path);
	if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
	if (!existsSync(file)) file = join(dist, '404.html');
	response.writeHead(existsSync(join(dist, path)) ? 200 : 404, { 'content-type': types[extname(file)] ?? 'application/octet-stream' });
	response.end(readFileSync(file));
});
await new Promise((resolve) => server.listen(0, resolve));
const origin = `http://localhost:${server.address().port}`;

const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
const problems = [];
for (const [width, height] of [[1280, 800], [390, 800]]) {
	for (const scheme of ['light', 'dark']) {
		const context = await browser.newContext({ viewport: { width, height }, colorScheme: scheme });
		const page = await context.newPage();
		for (const path of pages) {
			await page.goto(`${origin}${base}${path}`, { waitUntil: 'load' });
			await page.evaluate(axeSource);
			const result = await page.evaluate(() => axe.run(document, { resultTypes: ['violations'] }));
			for (const violation of result.violations) {
				problems.push(`${path} (${width}px, ${scheme}): ${violation.id} (${violation.impact}), ${violation.nodes.length} nodes, e.g. ${violation.nodes[0].target.join(' ')}`);
			}
		}
		await context.close();
	}
}
await browser.close();
server.close();
console.log(`${pages.length} pages checked at 2 widths and 2 themes`);
console.log(problems.length ? [...new Set(problems)].join('\n') : 'no accessibility violations');
process.exit(problems.length ? 1 : 0);
