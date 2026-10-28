# TopDownTemplate

A stylized top-down 3D game template for Godot 4.8 (.NET): a hand-painted meadow with grass, trees, and water, a day and night cycle, a character, a camera rig, and a pause panel. Copy it, rename it, and start a game.

## Start a new game

1. Close Godot, copy the whole project folder, and delete `.godot`, `builds`, and `.git` from the copy.
2. In the copy, run the rename script once with the Godot .NET executable. Add `--dry-run` first to see what it would change:

   ```
   godot --headless --path . --script res://tools/rename_project.gd -- "Studio Name" GameName
   ```

3. Open the project in Godot and click Build Project.

## Requirements

- Godot 4.8 (.NET build)
- .NET SDK 10

## Folders

| Folder | What it holds |
|---|---|
| `art/` | The art library: models, materials, shaders, and textures. It holds no scripts and never refers to anything outside itself. See `art/README.md`. |
| `art_source/` | The source files the art is made from, such as Blender and Krita files. |
| `levels/` | Scenes you play: the hand-built meadow and the generated level. |
| `src/` | All C# code. A folder is a namespace. |
| `tools/` | Editor scripts for the project itself, such as the audit. |
| `ui/` | The theme and the interface scenes. |
| `world/` | The scenes a level is made from: the camera rig, the environment, the player, the ground data, and the generator. |

## Conventions

- Files and folders outside `src/` are `snake_case`. Inside `src/`, folders and C# files are `PascalCase`, and a file is named after the class in it.
- Nodes are `PascalCase`. Input actions and shader globals are `snake_case`.
- C# uses file-scoped namespaces, nullable reference types, and one namespace root, the project's name. Warnings are errors.
- Run `tools/audit_project.gd` from the Script editor (File > Run) before you commit. It checks the art boundary and the names above.

## Layers

The first layer is `World`, so a static prop dropped into a level needs no setting changed. A body's layer says what it is, and its mask says what it collides with.

| Layer | Physics | Render |
|---|---|---|
| 1 | World | World |
| 2 | Terrain | Terrain |
| 3 | Hazard | Foliage |
| 4 | Interactable | Water |
| 5 | Player | Characters |
| 6 | Enemy | Effects |
| 7 | Npc | |
| 8 | Destructible | |
| 9 | Hurtbox | |
| 10 | Projectile | |
| 11 | Pickup | |
| 12 | Sensor | |

## Window

The base size is 1920 by 1080 with the `canvas_items` stretch mode and the `expand` aspect, and the camera keeps its height. Any window shape is filled with no bars, and a wider one shows more of the world.
