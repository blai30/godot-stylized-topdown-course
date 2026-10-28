# Art library

Everything the game draws: models, materials, shaders, and textures. The folder is self-contained, so it can be copied into another game or kept in a repository of its own.

## Rules

- It holds no scripts. Optional scripts that use the art live in `src/` and are attached in `world/` or `levels/`.
- It never refers to `world/`, `levels/`, `ui/`, or `src/`. `tools/audit_project.gd` checks this.
- It keeps the name `art` at the project's root, because its shaders include each other by `res://art/...` paths.
- Its source files are in `art_source/`.

## What it needs from the project

The shaders read these shader globals, set in Project Settings under Globals:

| Global | Type | Used for |
|---|---|---|
| `wind_direction` | `vec2` | The way the wind blows. |
| `wind_strength` | `float` | How hard it blows. |
| `push_point` | `vec4` | Where grass bends away from the player. |
| `rim_color` | `vec4` color | The color of the soft rim light. |
| `rim_strength` | `float` | How strong the rim light is. |
| `cloud_texture` | `sampler2D` | The noise the cloud shadows are cut from. |
| `cloud_scale` | `float` | The size of a cloud shadow in meters. |
| `cloud_strength` | `float` | How dark a cloud shadow is. |

`character/character.tscn` has an `AnimationTree` with a blend space on `parameters/blend_position`: set it to the speed of the body and the character walks and runs. The tree is off in the saved scene, so a script turns it on.
