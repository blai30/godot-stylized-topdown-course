# Verification tooling

Course tooling, not part of the reader's template. It performs lessons in the real tools, captures the screenshots, and checks the site. It runs on Windows, macOS, and Linux, as the course does. Everything runs from a working area under the system temp folder (`<temp>/sgt-phase1/` and `<temp>/sgt-phase2/`; set `TEMP` to move it), never inside this repository. Nothing here moves the system mouse or presses real keys.

## Running

`scripts/sgt.py` is the one runner. It needs only Python 3.9 or newer.

```sh
python3 scripts/sgt.py reset lesson-06
python3 scripts/sgt.py godot lesson05 --snapshot lesson-04
python3 scripts/sgt.py blender lesson09 --user lesson-08 --save-user lesson-09
python3 scripts/sgt.py krita lesson13 --save-user lesson-13
python3 scripts/sgt.py chain module2 --from 7
```

- `reset` restores the workbench to a snapshot and clears the editor's remembered view state; `snapshot` saves the workbench as one.
- `godot` resets to a snapshot (if given), copies the drivers in, compiles the step script, and replays it in the editor.
- `chain module1|module2|module3` replays lessons in order across Krita, Blender, and Godot. Each lesson starts from the snapshot the one before saved, and the chain stops at the first failure. Lesson 8 changes only Blender's user folder, which is saved for lesson 9; lessons 10 and 12 reuse the user folder of the lesson before.
- On a Mac the runner holds the display awake while it runs (`caffeinate`), because a sleeping display stalls Blender and Krita.

Setup, once per machine:

1. Put a copy of Godot's .NET editor in `<temp>/sgt-phase1/godot-sc/`, with an empty file named `._sc_` beside the executable, so its settings stay in that folder. Set the editor's display scale to 100% in `editor_data/editor_settings-4.8.tres` (`interface/editor/appearance/display_scale = 2`); a Retina screen otherwise gets 200% and 2048 by 1200 captures.
2. Link or copy the lesson snapshots to `<temp>/sgt-phase1/snapshots`.
3. Install Blender and Krita in their default places, or point `SGT_BLENDER` and `SGT_KRITA` at them (`SGT_GODOT` for Godot).

## Godot

- `godot-driver/driver.gd` is an editor plugin that replays steps inside the Godot editor: menus, dialogs, Inspector properties, typing into the Shader Editor, and window captures. Input is synthetic and pushed into Godot's own viewport. It lives in a hidden `.capture/` folder of a workbench copy of the reference project, enabled through `[editor_plugins]` in that copy's `project.godot`. Its step results go to a log file (`CAPTURE_LOG`), not the Output panel, so captures of the Output panel stay clean.
- `godot-driver/game_driver.gd` does the same inside the running game: an autoload (`GameDriver`, registered only in the workbench) that injects keys and the mouse wheel through `Input.parse_input_event` and saves frames. The editor run passes it a steps file and a log file through environment variables.
- `steps/` holds the step lists, written in Python (`steps.py` has the shared helpers) and compiled to one JSON object per line. Each lesson has a `lessonNN.py`; `probe*.py` scripts read labels and options from the real UI. Probe output goes to `editor.log`; a multi-line `print` shows only its first line when searched with grep.
- Godot shows each menu and dialog as its own desktop window, and opens a context menu at the system cursor, so a right-click lands on the desktop of whoever is at the computer. The step scripts avoid right-clicks, except `lesson02.py`, which verifies the FileSystem dock's menu once; lessons after it make folders directly. Single-window mode (`interface/editor/display/single_window_mode`) keeps menus inside the editor, but it also stops the running game from embedding in the Game tab, and the game then opens as its own desktop window, so the editor stays in the default multi-window mode.
- `scripts/sync_reference.py <snapshot folder> reference` copies a snapshot into `reference/` without the drivers, their `project.godot` entries, or the `.godot` cache, with LF line endings.
- `scripts/create_project.gd` writes `project.godot` the way the 4.8 Project Manager does. Since Phase 2 the project is created by the real Project Manager instead (below), and the two agree.

## The Project Manager

The editor plugin cannot run in the Project Manager. Start Godot with `--project-manager --accessibility always`: Godot then exposes its controls through AccessKit, and `scripts/uia.ps1` lists, invokes, and sets them through Windows UI Automation. Text fields that react to typing get their characters from `scripts/post-input.ps1`, which posts `WM_CHAR` messages to Godot's window only. Posted mouse clicks are ignored by Godot, so buttons are invoked through UI Automation. `scripts/capture-window.ps1` saves a window with `PrintWindow`. These three scripts are the only Windows-only tools left, and only lessons 1 and 2 use them; rerunning those lessons on another system needs an equivalent (macOS and Linux expose the same AccessKit tree through their own accessibility APIs).

## Blender

- `blender-steps/driver.py` replays a lesson's steps (`blender-steps/lessonNN.py`, a generator of delays) in Blender's real interface. Blender runs with `--enable-event-simulate`, so the steps press keys and click with `Window.event_simulate` while input from the system is ignored; nothing touches the system mouse or keyboard. Captures come from Blender's screenshot operator.
- `sgt.py blender` runs a step script with Blender's user folder (preferences, startup file) in `<temp>/sgt-phase2/blender-user`, started from a saved folder in `blender-users` or `fresh` (a first launch). Every `BLENDER_USER_*` folder is created first: for a missing one, Blender 5.2 falls back to the owner's own folder.
- Simulated input has limits, and the lessons are written around them: there is no double-click (rename with F2), click-drag tool selection does not start (box select with B), a button takes a click only after the pointer has hovered it (`press()`), popups do not close when the pointer leaves (Esc), and after a file loads the first click only wakes the window (`wake()`). Positions are for Blender's default interface scale, 1.0, at 1920 by 1080 pixels.
- On a Retina Mac, Blender sizes its window in points and doubles the pixels, so the runner asks for 960 by 540 points and the driver sets the Resolution Scale to 0.5. A second window's size (the File Browser) is in points too, so `pixels()` converts it, and `save_button_x()` finds the browser's Save button.
- `scripts/rock_gui.py` is Phase 1's lesson 9 run, which used operators instead of hotkeys; `rock_proto.py`, `labels9.py`, and `hotkeys.py` read labels, defaults, and the keymap from Blender itself.

## Krita

- `krita-driver/` is a Krita Python plugin that replays a lesson's steps (`krita-steps/lessonNN.py`) inside Krita: synthetic Qt events to Krita's own widgets, and window grabs. The canvas needs a FocusIn event before it takes input, and Krita's shape and selection tools finish a shape only on a spontaneous release, so the driver marks its mouse events spontaneous and delivers them with `QApplication.notify`.
- Captures are screen grabs of the window's rectangle (`QScreen.grabWindow`), so canvas overlays (grid, selection outline) and dialogs are in them; `QWidget.grab()` leaves the overlays out. A high-density screen grabs more pixels than the window has, and the driver scales the image back to the window's size.
- The runner turns off Krita's native file dialogs (`DontUseNativeFileDialog=true` under `[File Dialogs]` in `kritarc`), so `file_dialog()` fills in Qt's own dialog the same way on every system. The reader sees their system's dialog; the lesson text does not depend on its look.
- `sgt.py krita` installs the plugin and runs Krita. Krita keeps its settings in fixed places (`%LOCALAPPDATA%\kritarc` and `%APPDATA%\krita` on Windows, `~/Library/Preferences/kritarc` and `~/Library/Application Support/krita` on a Mac, `~/.config/kritarc` and `~/.local/share/krita` on Linux), so the runner moves any existing ones to `<temp>/sgt-phase2/krita-backup`, runs, deletes everything the run created, and moves the originals back. It refuses to run while an old backup exists. On a Mac, Krita runs at `QT_SCALE_FACTOR=0.75`, so its 1920 by 1080 window fits a laptop screen.
- Krita reads the real keyboard's modifier state during a canvas drag, so a key held on the computer during a run can spoil one selection; the lesson 7 script checks every swatch's selection and retries.
- Slider fields (brush Size, Opacity, Fade Length, Spacing) take a typed number after a right-click on the field's text box, once its text shows selected (`slider()`). When Krita is not the active window on the desktop, the field commits after the first key, and the driver must not change the desktop's focus, so `slider()` then sets the value directly and logs `SLIDER SET DIRECTLY`; typing itself is verified in the runs where Krita had focus. Digits sent before the field is typing are Krita shortcuts (1 resets the zoom, 4 to 6 turn the canvas).
- Buttons that open a modal dialog are clicked with `click_later()`, so the steps keep ticking.
- `--save-user lesson-13` keeps a copy of Krita's settings and resources after a run under `<temp>/sgt-phase2/krita-users`, and `--user lesson-13` starts from it, so lesson 14 has the brushes lesson 13 saved, as on a reader's machine. `krita-steps/ground_painting.py` holds the steps lessons 13 and 14 share.

## Assets and code

- `scripts/make_assets.py` crops captures into `site/src/assets/lessons/` for lessons 1 to 12; `scripts/make_assets_ground.py` does lessons 13 to 17 from a Module 3 chain run. Captures of file dialogs are cropped to their path and name fields, because their folder views show the computer's own folders. `scripts/make_assets_lesson18.py` does the same for lesson 18 (it needs Pillow).
- `scripts/export_pieces.py <lesson> [files...]` writes a lesson's code pieces from the same step script that typed them into the editor, and copies its checkpoint files from the lesson's snapshot, into `site/src/checkpoints/`.
- `scripts/make_grass.py` makes the reference grass texture (512 pixels for 2 meters, seamless).

## Site checks

- `scripts/check-links.mjs dist [base] [own origin]`: every internal link and anchor must exist, and every external link must answer. For a sub-path build, pass the base path (`/StylizedGameTemplateCourse/`) and the site's origin, which is skipped until it is published.
- `scripts/check-accessibility.mjs dist [base]`: axe-core on every page at a desktop and a phone width, in both themes. Run `npm install` in `tools/verification` first, and set `CHROME` to a Chromium executable if Playwright's is not installed.
- `scripts/cspell.json`: American English spelling, run with `npx cspell --config tools/verification/scripts/cspell.json "site/src/**/*.mdx"`.
- Accessibility was checked with axe-core in a browser, in both themes, at desktop and phone widths, with solutions, the image viewer, and search open.

## Side effects outside the temp folder

A running game writes its log to Godot's user data folder for the project: `%APPDATA%\Godot\app_userdata\TopDownTemplate\logs` on Windows, `~/Library/Application Support/Godot/app_userdata/TopDownTemplate` on a Mac, `~/.local/share/godot/app_userdata/TopDownTemplate` on Linux. Delete that folder after a verification session.

Some scripts, such as `make_assets.py`, still hold absolute paths from the first machine they ran on; set them for your machine before running.
