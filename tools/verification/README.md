# Verification tooling

Course tooling, not part of the reader's template. It performs lessons in the real tools, captures the screenshots, and checks the site. Everything runs from a working area under the system temp folder (`%TEMP%\sgt-phase1\`), never inside this repository.

## Godot

- `godot-driver/` is an editor plugin that replays steps inside the Godot editor: menus, dialogs, Inspector properties, typing into the Shader Editor, and window captures. Input is synthetic and pushed into Godot's own viewport, so the system mouse and keyboard are never touched. It lives in a hidden `.capture/` folder of a workbench copy of the reference project, enabled through `[editor_plugins]` in that copy's `project.godot`.
- `steps/` holds the step lists, written in Python (`steps.py` has the helpers) and compiled to one JSON object per line. Run one with `python steps/lesson15b.py <steps folder> <out.jsonl>`.
- `scripts/run-steps.ps1` opens the workbench in a self-contained Godot copy (a `._sc_` file beside the executable keeps editor settings fresh and separate) at 1920 by 1080 and 100% editor scale, and replays a steps file.
- `scripts/reset-workbench.ps1` restores the workbench to a lesson snapshot and clears the editor's remembered view state.
- `scripts/sync_reference.py` copies the workbench into `reference/` without the driver or the `.godot` cache, with LF line endings.
- `scripts/create_project.gd` writes `project.godot` exactly as the 4.8 Project Manager does.

## Blender

- `scripts/rock_gui.py` performs lesson 9 in Blender's real interface on a timer and saves each state with Blender's screenshot operator. `rock_proto.py`, `labels9.py`, and `hotkeys.py` read operator labels, defaults, and the default keymap from Blender itself.

## Assets and code

- `scripts/make_assets.py` crops captures into `site/src/assets/lessons/`.
- `scripts/export_pieces.py` writes lesson code pieces from the same step scripts that typed them into the editor, into `site/src/checkpoints/`.
- `scripts/make_grass.py` makes the reference grass texture (512 pixels for 2 meters, seamless).

## Site checks

- `scripts/check-links.mjs dist`: every internal link and anchor must exist, and every external link must answer.
- `scripts/cspell.json`: American English spelling, run with `npx cspell --config tools/verification/scripts/cspell.json "site/src/**/*.mdx"`.
- Accessibility was checked with axe-core in a browser, in both themes, at desktop and phone widths, with solutions, the image viewer, and search open.

Some scripts still hold absolute paths from the first machine they ran on; set them for your machine before running.
