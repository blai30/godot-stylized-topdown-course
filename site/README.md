# Course site

The course website, built with [Astro](https://astro.build) and [Starlight](https://starlight.astro.build).

| Command | What it does |
|---|---|
| `npm install` | Installs the dependencies |
| `npm run dev` | Starts a local server at `localhost:4321` that reloads on changes |
| `npm run build` | Builds the static site into `dist/` |
| `npm run preview` | Serves the built site locally |

## Where things live

- `src/content/docs/`: the pages. Lessons sit in one folder per module.
- `src/data/syllabus.ts`: every lesson's number, title, and folder. Lesson pages must match it, or the build fails.
- `src/checkpoints/<lesson>/`: code shown in lessons, copied from the verified reference project rather than typed.
- `src/assets/lessons/<lesson>/`: screenshots captured from the real tools.
- `src/components/`: `Solution`, `Kbd`, `LessonMeta`, `Checkpoint`, `Figure`, and Starlight overrides.
