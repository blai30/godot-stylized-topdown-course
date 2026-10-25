using Godot;

namespace TopDownTemplate.Tools;

// Adds the day animation's tracks from the tables below. Open world_environment.tscn, then run it from the Script editor with File > Run.
[Tool]
public partial class BuildDay : EditorScript
{
	private const string AnimationName = "day";
	private const double DayLength = 60.0;

	// The sun's color and energy. Times run from 0 (midnight) to 1; noon is 0.5.
	private readonly record struct LightKey(float Time, string Color, float Energy);

	// Where the light points, in degrees: the sun from sunrise to sunset, the moon otherwise.
	private readonly record struct DirectionKey(float Time, Vector3 Rotation);

	// The sky, the fog, the glow, and the color grade.
	private readonly record struct LookKey(
		float Time, string Zenith, string Horizon, string Fog, float Saturation, float Glow,
		string ShadowTint, string HighlightTint, float GradeStrength, float GradeSaturation,
		string RimColor, float RimStrength);

	// The moon fades out before sunrise and in after sunset. The sun and the moon swap while the energy is 0, so nothing jumps.
	private static readonly LightKey[] Lights =
	[
		new(0.00f, "#78B8FF", 0.45f), new(0.11f, "#78B8FF", 0.45f), new(0.15f, "#78B8FF", 0f),
		new(0.1501f, "#FFA8C7", 0f), new(0.20f, "#FFBDCC", 3.0f), new(0.27f, "#FFDAA4", 0.75f),
		new(0.50f, "#FFE2AD", 0.85f), new(0.73f, "#FFD8A2", 0.8f), new(0.80f, "#FF8F4C", 4.3f),
		new(0.85f, "#FF8F4C", 0f), new(0.8501f, "#78B8FF", 0f), new(0.89f, "#78B8FF", 0.45f),
		new(1.00f, "#78B8FF", 0.45f),
	];

	private static readonly DirectionKey[] Directions =
	[
		new(0.00f, new(-50f, 200f, 0f)), new(0.15f, new(-50f, 200f, 0f)), new(0.1501f, new(0f, 90f, 0f)),
		new(0.20f, new(-13.8f, 109.3f, 0f)), new(0.27f, new(-31.8f, 136.3f, 0f)), new(0.35f, new(-48.5f, 167.1f, 0f)),
		new(0.50f, new(-62f, 225f, 0f)), new(0.65f, new(-48.5f, 244.3f, 0f)), new(0.73f, new(-31.8f, 254.6f, 0f)),
		new(0.80f, new(-13.8f, 263.6f, 0f)), new(0.85f, new(0f, 270f, 0f)), new(0.8501f, new(-50f, 200f, 0f)),
		new(1.00f, new(-50f, 200f, 0f)),
	];

	private static readonly LookKey[] Looks =
	[
		new(0.00f, "#142961", "#1F4073", "#1A335C", 0.85f, 0.45f, "#1FADFF", "#99BFFF", 0.60f, 0.30f, "#8FA3E0", 0.25f),
		new(0.12f, "#293875", "#8070A8", "#4C5285", 0.85f, 0.45f, "#7380FF", "#CCB2FF", 0.55f, 0.45f, "#A99BD6", 0.25f),
		new(0.15f, "#3F4E9E", "#FFA3D6", "#D19ECC", 1.00f, 0.45f, "#C79EFF", "#FF73BF", 0.55f, 1.00f, "#FFADCC", 0.40f),
		new(0.20f, "#5B78C9", "#FFADDB", "#F2B8DB", 1.00f, 0.45f, "#C79EFF", "#FF73BF", 0.50f, 1.00f, "#FFB8DB", 0.40f),
		new(0.27f, "#58A6F2", "#A8D1FF", "#BDDBFF", 1.00f, 0.00f, "#FFFFFF", "#FFFFFF", 0.00f, 1.00f, "#CFE6FF", 0.30f),
		new(0.50f, "#4FA9FF", "#8FC7FF", "#B8DBFF", 1.00f, 0.00f, "#FFFFFF", "#FFFFFF", 0.00f, 1.00f, "#C6E4FF", 0.30f),
		new(0.73f, "#5AA8F5", "#ADD1FA", "#C2DBFA", 1.00f, 0.00f, "#FFFFFF", "#FFFFFF", 0.00f, 1.00f, "#D2E8FF", 0.30f),
		new(0.80f, "#7A70D9", "#FFB8A3", "#D1A8A3", 0.78f, 0.45f, "#D999F2", "#FF8C47", 0.30f, 0.90f, "#FF9E66", 0.45f),
		new(0.85f, "#594CA6", "#F29980", "#99738C", 0.95f, 0.45f, "#CC8CFF", "#FFA866", 0.40f, 0.95f, "#B79AD0", 0.30f),
		new(1.00f, "#142961", "#1F4073", "#1A335C", 0.85f, 0.45f, "#1FADFF", "#99BFFF", 0.60f, 0.30f, "#8FA3E0", 0.25f),
	];

	public override void _Run()
	{
		var root = GetScene();
		var animation = root.GetNode<AnimationPlayer>("Day").GetAnimation(AnimationName);

		foreach (var key in Lights)
		{
			Insert(animation, "Sun:light_color", key.Time, Color.FromHtml(key.Color));
			Insert(animation, "Sun:light_energy", key.Time, key.Energy);
		}

		foreach (var key in Directions)
		{
			Insert(animation, "Sun:rotation_degrees", key.Time, key.Rotation);
		}

		foreach (var key in Looks)
		{
			Insert(animation, ".:environment:sky:sky_material:shader_parameter/zenith_color", key.Time, Color.FromHtml(key.Zenith));
			Insert(animation, ".:environment:sky:sky_material:shader_parameter/horizon_color", key.Time, Color.FromHtml(key.Horizon));
			Insert(animation, ".:environment:fog_light_color", key.Time, Color.FromHtml(key.Fog));
			Insert(animation, ".:environment:adjustment_saturation", key.Time, key.Saturation);
			Insert(animation, ".:environment:glow_intensity", key.Time, key.Glow);
			Insert(animation, "Grade/Screen:material:shader_parameter/shadow_tint", key.Time, Color.FromHtml(key.ShadowTint));
			Insert(animation, "Grade/Screen:material:shader_parameter/highlight_tint", key.Time, Color.FromHtml(key.HighlightTint));
			Insert(animation, "Grade/Screen:material:shader_parameter/strength", key.Time, key.GradeStrength);
			Insert(animation, "Grade/Screen:material:shader_parameter/saturation", key.Time, key.GradeSaturation);
			Insert(animation, "Day:RimColor", key.Time, Color.FromHtml(key.RimColor));
			Insert(animation, "Day:RimStrength", key.Time, key.RimStrength);
		}

		EditorInterface.Singleton.MarkSceneAsUnsaved();
		GD.Print($"The {AnimationName} animation has {animation.GetTrackCount()} tracks.");
	}

	// Puts a key on the track for a property, adding the track the first time.
	private static void Insert(Animation animation, string path, float time, Variant value)
	{
		var track = animation.FindTrack(path, Animation.TrackType.Value);
		if (track == -1)
		{
			track = animation.AddTrack(Animation.TrackType.Value);
			animation.TrackSetPath(track, path);
		}

		animation.TrackInsertKey(track, time * DayLength, value);
	}
}
