// Lesson progress lives only in this browser's localStorage: no accounts, no backend.
const storageKey = 'hand-made-top-down:done-lessons';
export const progressEvent = 'lesson-progress';

export function readDone(): Set<string> {
	try {
		const stored: unknown = JSON.parse(localStorage.getItem(storageKey) ?? '[]');
		return new Set(Array.isArray(stored) ? stored.filter((id) => typeof id === 'string') : []);
	} catch {
		return new Set();
	}
}

export function setDone(lessonId: string, done: boolean): void {
	const lessons = readDone();
	if (done) lessons.add(lessonId);
	else lessons.delete(lessonId);
	localStorage.setItem(storageKey, JSON.stringify([...lessons]));
	document.dispatchEvent(new CustomEvent(progressEvent));
}

// Runs the callback now, whenever this page changes progress, and whenever another tab does.
export function onProgressChange(callback: (done: Set<string>) => void): void {
	const update = () => callback(readDone());
	update();
	document.addEventListener(progressEvent, update);
	window.addEventListener('storage', (event) => {
		if (event.key === storageKey) update();
	});
}
