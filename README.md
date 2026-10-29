# Handmade Meadow

A beginner course that teaches you to build, entirely by hand, a reusable Godot template for stylized top-down 3D games: a hand-painted meadow with grass, trees, and water, a day and night cycle, an animated character, a follow camera, and your own art library. You make every model, texture, shader, scene, and script yourself, then copy the result to start any game.

Read the course at https://blai30.github.io/godot-stylized-topdown-course/.

## What you need

- Godot 4.8 (.NET build) and the .NET SDK it requires
- Blender 5.2 and Krita
- Git and Git LFS

The first lesson walks through installing everything.

## What is in this repository

| Folder | Contents |
|---|---|
| `site/` | The course website (Astro and Starlight). |
| `reference/` | The course's own build of the template, made by following the lessons. It proves every step works and provides the screenshots and solution code. |
| `docs/` | The course spec, the phase and module reports, and the target-look reference images. |
| `tools/verification/` | Tooling that performs the lessons in Godot, Blender, and Krita, captures the screenshots, and checks the site. |

Binary files are stored with Git LFS. Run `git lfs install` once before cloning.

## Build the site locally

```sh
cd site
npm ci
npm run dev
```

`npm run build` writes the static site to `site/dist`. The `deploy` workflow publishes it to GitHub Pages under the repository's name.

## License

The source code is under the MIT License (`LICENSE`). Everything else the author made, including the lesson text, images, models, and textures, is dedicated to the public domain under CC0 1.0 (`LICENSE-CC0`), free for any use. Third-party material keeps its own license; see `CREDITS.md`.
