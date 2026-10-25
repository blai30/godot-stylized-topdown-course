// The whole course in order: the syllabus page, lesson prerequisites, and module folders all read from here.
export type Module = {
	number: number;
	title: string;
	directory: string;
	lessons: { number: number; title: string; slug: string }[];
};

export const modules: Module[] = [
	{
		number: 1,
		title: 'Foundations',
		directory: 'foundations',
		lessons: [
			{ number: 1, title: 'Install everything', slug: 'install-everything' },
			{ number: 2, title: 'Create the project', slug: 'create-the-project' },
			{ number: 3, title: 'Project settings for a top-down 3D game', slug: 'project-settings' },
			{ number: 4, title: 'A first scene: ground, sun, and sky', slug: 'a-first-scene' },
			{ number: 5, title: 'The camera rig and your first C# script', slug: 'the-camera-rig' },
			{ number: 6, title: 'A player capsule that walks', slug: 'a-player-capsule' },
		],
	},
	{
		number: 2,
		title: 'Color and the first model',
		directory: 'color-and-first-model',
		lessons: [
			{ number: 7, title: 'Choose your palette', slug: 'choose-your-palette' },
			{ number: 8, title: 'Blender for Godot', slug: 'blender-for-godot' },
			{ number: 9, title: 'Model a small rock', slug: 'model-a-small-rock' },
			{ number: 10, title: 'Color the rock and export it', slug: 'color-and-export-the-rock' },
			{ number: 11, title: 'Import the rock into Godot', slug: 'import-the-rock' },
			{ number: 12, title: 'A large rock and variants', slug: 'a-large-rock-and-variants' },
		],
	},
	{
		number: 3,
		title: 'The ground',
		directory: 'the-ground',
		lessons: [
			{ number: 13, title: 'Draw the grass detail with code', slug: 'generate-grass-detail' },
			{ number: 14, title: 'Paint dirt and sand to match', slug: 'paint-dirt-and-sand' },
			{ number: 15, title: 'Your first shader', slug: 'your-first-shader' },
			{ number: 16, title: 'Tile meshes, a MeshLibrary, and a GridMap', slug: 'tiles-and-gridmap' },
			{ number: 17, title: 'Soft tile edges', slug: 'soft-tile-edges' },
			{ number: 18, title: 'Ground tiles as custom resources', slug: 'ground-tile-resources' },
		],
	},
	{
		number: 4,
		title: 'Light and mood',
		directory: 'light-and-mood',
		lessons: [
			{ number: 19, title: 'The Environment resource', slug: 'the-environment' },
			{ number: 20, title: 'The sun and its shadows', slug: 'the-sun' },
			{ number: 21, title: 'Keyframing the day', slug: 'keyframing-the-day' },
			{ number: 22, title: 'DayClock: dusk, dawn, and moonlight', slug: 'day-clock' },
			{ number: 23, title: 'Stylized lighting in a shared shader include', slug: 'stylized-lighting' },
		],
	},
	{
		number: 5,
		title: 'Trees',
		directory: 'trees',
		lessons: [
			{ number: 24, title: 'Model a trunk and branches', slug: 'model-a-trunk' },
			{ number: 25, title: 'Paint a leaf atlas', slug: 'paint-a-leaf-atlas' },
			{ number: 26, title: 'Leaf cards and transferred normals', slug: 'leaf-cards' },
			{ number: 27, title: 'The foliage shader and wind', slug: 'the-foliage-shader' },
			{ number: 28, title: 'The tree scene: plant a grove', slug: 'plant-a-grove' },
			{ number: 29, title: 'A second species: a pine', slug: 'a-pine' },
		],
	},
	{
		number: 6,
		title: 'Grass and flowers',
		directory: 'grass-and-flowers',
		lessons: [
			{ number: 30, title: 'Model a grass clump and two flowers', slug: 'model-grass-and-flowers' },
			{ number: 31, title: 'The grass shader', slug: 'the-grass-shader' },
			{ number: 32, title: 'Scatter grass from the tiles', slug: 'scatter-grass' },
			{ number: 33, title: 'Grass that parts around the player', slug: 'grass-that-parts' },
			{ number: 34, title: 'Decoratives: pebbles, mushrooms, and dirt patches', slug: 'decoratives' },
		],
	},
	{
		number: 7,
		title: 'The character',
		directory: 'the-character',
		lessons: [
			{ number: 35, title: 'Design a character that reads from above', slug: 'design-the-character' },
			{ number: 36, title: 'Blockout', slug: 'character-blockout' },
			{ number: 37, title: 'Refine the body, head, and clothing', slug: 'refine-the-character' },
			{ number: 38, title: 'UVs and painting', slug: 'character-uvs-and-painting' },
			{ number: 39, title: 'The armature on Godot humanoid bone names', slug: 'the-armature' },
			{ number: 40, title: 'Skinning with weight painting', slug: 'skinning' },
			{ number: 41, title: 'Export your character and import it with a BoneMap', slug: 'import-with-a-bonemap' },
			{ number: 42, title: 'Import the Universal Animation Library', slug: 'import-ual' },
			{ number: 43, title: 'AnimationTree: walk the meadow', slug: 'animation-tree' },
		],
	},
	{
		number: 8,
		title: 'Water',
		directory: 'water',
		lessons: [
			{ number: 44, title: 'Model the bank kit', slug: 'model-the-bank-kit' },
			{ number: 45, title: 'The water shader: depth and color', slug: 'water-depth' },
			{ number: 46, title: 'The water shader: waves, refraction, and the shoreline', slug: 'water-waves' },
			{ number: 47, title: 'Update shore: placing the bank pieces', slug: 'update-shore' },
			{ number: 48, title: 'Water the player cannot walk into', slug: 'water-collision' },
		],
	},
	{
		number: 9,
		title: 'Procedural worlds',
		directory: 'procedural-worlds',
		lessons: [
			{ number: 49, title: 'Noise as a resource', slug: 'noise' },
			{ number: 50, title: 'Generating ground into the GridMap', slug: 'generating-ground' },
			{ number: 51, title: 'Scattering props by rules', slug: 'scattering-props' },
			{ number: 52, title: 'Runtime, editor, and hand-painted areas together', slug: 'runtime-and-editor' },
		],
	},
	{
		number: 10,
		title: 'Polish',
		directory: 'polish',
		lessons: [
			{ number: 53, title: 'Cloud shadows', slug: 'cloud-shadows' },
			{ number: 54, title: 'More nature: bushes and a glowing mineral rock', slug: 'more-nature' },
			{ number: 55, title: 'A Theme and a pause panel', slug: 'theme-and-pause-panel' },
			{ number: 56, title: 'Performance and exporting a build', slug: 'performance-and-export' },
		],
	},
	{
		number: 11,
		title: 'Make it a template',
		directory: 'make-it-a-template',
		lessons: [
			{ number: 57, title: 'Clean up and draw the art library boundary', slug: 'clean-up' },
			{ number: 58, title: 'Copy the template into a new game', slug: 'copy-the-template' },
			{ number: 59, title: 'Bonus: a grid cursor for tactics games', slug: 'bonus-grid-cursor' },
			{ number: 60, title: 'Bonus: click to move for action RPGs', slug: 'bonus-click-to-move' },
			{ number: 61, title: 'Bonus: tile-snapped movement for farming games', slug: 'bonus-tile-movement' },
		],
	},
];

export const lessons = modules.flatMap((module) =>
	module.lessons.map((lesson) => ({ ...lesson, module, id: `${module.directory}/${lesson.slug}` })),
);

export function lessonByNumber(number: number) {
	const lesson = lessons.find((candidate) => candidate.number === number);
	if (!lesson) throw new Error(`No lesson ${number} in the syllabus.`);
	return lesson;
}

