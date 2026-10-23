# Verification tooling

Course tooling, not part of the reader's template. It performs lessons in the real tools, captures the screenshots, and checks the site. Everything runs from a working area under the system temp folder (`%TEMP%\sgt-phase1\` and `%TEMP%\sgt-phase2\`), never inside this repository. Nothing here moves the system mouse or presses real keys.

## Godot

- `godot-driver/driver.gd` is an editor plugin that replays steps inside the Godot editor: menus, dialogs, Inspector properties, typing into the Shader Editor, and window captures. Input is synthetic and pushed into Godot's own viewport. It lives in a hidden `.capture/` folder of a workbench copy of the reference project, enabled through `[editor_plugins]` in that copy's `project.godot`. Its step results go to a log file (`CAPTURE_LOG`), not the Output panel, so captures of the Output panel stay clean.
- `godot-driver/game_driver.gd` does the same inside the running game: an autoload (`GameDriver`, registered only in the workbench) that injects keys and the mouse wheel through `Input.parse_input_event` and saves frames. The editor run passes it a steps file and a log file through environment variables.
- `steps/` holds the step lists, written in Python (`steps.py` has the shared helpers) and compiled to one JSON object per line. Each lesson has a `lessonNN.py`; `probe*.py` scripts read labels and options from the real UI.
- `scripts/run-chain.ps1 -From 3 -To 6` replays lessons in order, each from the snapshot the one before saved, stops at the first failure or script error, and keeps each lesson's logs.
- `scripts/run-lesson.ps1 -Script lesson05 -Snapshot lesson-04` resets the workbench to a snapshot, copies the drivers in, compiles the steps, and replays them. It uses `run-steps.ps1`, which opens the workbench in a self-contained Godot copy (a `._sc_` file beside the executable keeps editor settings separate) at 1920 by 1080 and 100% editor scale, and closes it when the driver logs `[capture] done`.
- Godot shows each menu and dialog as its own desktop window, and opens a context menu at the system cursor, so a right-click lands on the desktop of whoever is at the computer. The step scripts avoid right-clicks, except `lesson02.py`, which verifies the FileSystem dock's menu once; lessons after it make folders directly. Single-window mode (`interface/editor/display/single_window_mode`) keeps menus inside the editor, but it also stops the running game from embedding in the Game tab, and the game then opens as its own desktop window, so the editor stays in the default multi-window mode.
- `scripts/reset-workbench.ps1` restores the workbench to a lesson snapshot (`%TEMP%\sgt-phase1\snapshots\lesson-NN`) and clears the editor's remembered view state.
- `scripts/sync_reference.py` copies the workbench into `reference/` without the drivers, their `project.godot` entries, or the `.godot` cache, with LF line endings.
- `scripts/create_project.gd` writes `project.godot` the way the 4.8 Project Manager does. Since Phase 2 the project is created by the real Project Manager instead (below), and the two agree.

## The Project Manager

The editor plugin cannot run in the Project Manager. Start Godot with `--project-manager --accessibility always`: Godot then exposes its controls through AccessKit, and `scripts/uia.ps1` lists, invokes, and sets them through Windows UI Automation. Text fields that react to typing get their characters from `scripts/post-input.ps1`, which posts `WM_CHAR` messages to Godot's window only. Posted mouse clicks are ignored by Godot, so buttons are invoked through UI Automation. `scripts/capture-window.ps1` saves a window with `PrintWindow`.

## Blender

- `scripts/rock_gui.py` performs lesson 9 in Blender's real interface on a timer and saves each state with Blender's screenshot operator. `rock_proto.py`, `labels9.py`, and `hotkeys.py` read operator labels, defaults, and the default keymap from Blender itself.

## Assets and code

- `scripts/make_assets.py` crops captures into `site/src/assets/lessons/`.
- `scripts/export_pieces.py <lesson> [files...]` writes a lesson's code pieces from the same step script that typed them into the editor, and copies its checkpoint files from the lesson's snapshot, into `site/src/checkpoints/`.
- `scripts/make_grass.py` makes the reference grass texture (512 pixels for 2 meters, seamless).

## Site checks

- `scripts/check-links.mjs dist`: every internal link and anchor must exist, and every external link must answer.
- `scripts/cspell.json`: American English spelling, run with `npx cspell --config tools/verification/scripts/cspell.json "site/src/**/*.mdx"`.
- Accessibility was checked with axe-core in a browser, in both themes, at desktop and phone widths, with solutions, the image viewer, and search open.

## Side effects outside the temp folder

A running game writes its log to `%APPDATA%\Godot\app_userdata\TopDownTemplate\logs`. Delete that folder after a verification session.

Some scripts still hold absolute paths from the first machine they ran on; set them for your machine before running.
