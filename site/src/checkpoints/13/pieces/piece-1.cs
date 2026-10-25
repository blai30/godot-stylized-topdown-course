using System;
using Godot;

namespace TopDownTemplate.Tools;

// Draws the grass detail, a gray image of overlapping blades that the ground shader tints. Run it from the Script editor with File > Run.
[Tool]
public partial class GrassDetail : EditorScript
{
	private const int Size = 1024;
	private const string Path = "res://art/ground/grass_detail.png";

	private readonly float[] _values = new float[Size * Size];

	public override void _Run()
	{
		// The gaps between the blades start darker than the blades.
		Array.Fill(_values, 0.72f);
		Save();
	}

	private void Save()
	{
		var bytes = new byte[Size * Size];
		for (var i = 0; i < bytes.Length; i++)
		{
			bytes[i] = (byte)(Math.Clamp(_values[i], 0f, 1f) * 255f);
		}

		var image = Image.CreateFromData(Size, Size, false, Image.Format.L8, bytes);
		image.SavePng(ProjectSettings.GlobalizePath(Path));
		EditorInterface.Singleton.GetResourceFilesystem().Scan();
		GD.Print($"Saved {Path}");
	}
}
