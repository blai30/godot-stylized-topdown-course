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
		DrawBlade(Size / 2f, Size / 2f, -MathF.PI / 2f, 150f, 40f, 0.15f, 0.9f);
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

	private static float Range(Random random, float low, float high)
	{
		return low + random.NextSingle() * (high - low);
	}

	private static float Smooth(float low, float high, float x)
	{
		var t = Math.Clamp((x - low) / (high - low), 0f, 1f);
		return t * t * (3f - 2f * t);
	}

	// How much of a pixel a blade covers, 0 to 1, and how far along the blade the pixel is. A blade is curved, widest
	// near its root, and tapers to a point.
	private static (float Cover, float Tip) Cover(float dx, float dy, float heading, float length, float width, float bend)
	{
		var along = dx * MathF.Cos(heading) + dy * MathF.Sin(heading);
		var across = dy * MathF.Cos(heading) - dx * MathF.Sin(heading) - bend * along * along / length;
		var tip = along / length;
		if (tip is < -0.1f or >= 1f)
		{
			return (0f, tip);
		}

		var half = width / 2f * MathF.Pow(Math.Clamp(1f - tip, 0f, 1f), 0.8f) * Smooth(-0.1f, 0.12f, tip);
		var edge = 1f - MathF.Abs(across) / MathF.Max(half, 1e-6f);
		return (Smooth(0f, 0.1f, edge), tip);
	}

	private void DrawBlade(float rootX, float rootY, float heading, float length, float width, float bend, float shade)
	{
		var reach = (int)length + 6;
		for (var y = (int)rootY - reach; y <= (int)rootY + reach; y++)
		{
			for (var x = (int)rootX - reach; x <= (int)rootX + reach; x++)
			{
				var (cover, tip) = Cover(x + 0.5f - rootX, y + 0.5f - rootY, heading, length, width, bend);
				if (cover <= 0f)
				{
					continue;
				}

				// The picture wraps at its edges, so it tiles.
				var index = (((y % Size) + Size) % Size) * Size + ((x % Size) + Size) % Size;
				var color = shade * (0.97f + 0.06f * Math.Clamp(tip, 0f, 1f));
				_values[index] = _values[index] * (1f - cover) + color * cover;
			}
		}
	}
}
