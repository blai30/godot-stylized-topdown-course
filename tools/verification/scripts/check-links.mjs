// Checks every link in the built site: internal pages and #anchors must exist; external URLs must answer below 400.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const dist = process.argv[2];
const files = [];
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).forEach((entry) => {
	const path = join(dir, entry.name);
	if (entry.isDirectory()) walk(path);
	else if (entry.name.endsWith('.html')) files.push(path);
});
walk(dist);

const idsOf = new Map();
const ids = (file) => {
	if (!idsOf.has(file)) idsOf.set(file, new Set([...readFileSync(file, 'utf8').matchAll(/\sid="([^"]+)"/g)].map((match) => match[1])));
	return idsOf.get(file);
};
const pageFor = (pathname) => {
	const clean = decodeURIComponent(pathname).replace(/^\//, '');
	for (const candidate of [join(dist, clean, 'index.html'), join(dist, `${clean}.html`)]) {
		if (existsSync(candidate)) return candidate;
	}
	return existsSync(join(dist, clean)) ? join(dist, clean) : null;
};

const problems = [];
const external = new Map();
for (const file of files) {
	const page = relative(dist, file).split(sep).join('/');
	const html = readFileSync(file, 'utf8');
	for (const [, raw] of html.matchAll(/\shref="([^"]+)"/g)) {
		const href = raw.replaceAll('&amp;', '&');
		if (href.startsWith('mailto:') || href.startsWith('data:')) continue;
		if (/^https?:\/\//.test(href)) {
			if (!external.has(href)) external.set(href, page);
			continue;
		}
		const url = new URL(href, `http://site/${page}`);
		const target = pageFor(url.pathname);
		if (!target) {
			problems.push(`${page}: missing page ${href}`);
			continue;
		}
		if (url.hash && target.endsWith('.html') && !ids(target).has(decodeURIComponent(url.hash.slice(1)))) {
			problems.push(`${page}: missing anchor ${href}`);
		}
	}
}

const results = await Promise.all([...external].map(async ([href, from]) => {
	for (const method of ['HEAD', 'GET']) {
		try {
			const response = await fetch(href, { method, redirect: 'follow', headers: { 'user-agent': 'Mozilla/5.0 link-check' }, signal: AbortSignal.timeout(20000) });
			if (response.status < 400) return null;
			if (method === 'GET') return `${from}: ${response.status} ${href}`;
		} catch (error) {
			if (method === 'GET') return `${from}: ${error.name} ${href}`;
		}
	}
	return null;
}));
problems.push(...results.filter(Boolean));
console.log(`${files.length} pages, ${external.size} external links checked`);
console.log(problems.length ? problems.join('\n') : 'no broken links or anchors');
process.exit(problems.length ? 1 : 0);
