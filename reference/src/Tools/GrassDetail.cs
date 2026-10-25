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
		var random = new Random(404);
		// The gaps between the blades start darker than the blades.
		Array.Fill(_values, 0.72f);

		for (var cluster = 0; cluster < 150; cluster++)
		{
			var rootX = random.NextSingle() * Size;
			var rootY = random.NextSingle() * Size;
			// Blades point up the screen, fanned out.
			var heading = -MathF.PI / 2f + Range(random, -0.9f, 0.9f);
			var tone = Range(random, -0.04f, 0.04f);
			var blades = random.Next(4, 7);
			for (var order = 0; order < blades; order++)
			{
				// Drawn back to front: each blade a little lighter than the one behind it.
				var shade = 0.84f + 2f * tone + 0.05f * order / 5f;
				DrawBlade(
					rootX + Range(random, -13f, 13f),
					rootY + Range(random, -13f, 13f),
					heading + Range(random, -0.45f, 0.45f),
					Range(random, 114f, 176f),
					Range(random, 31f, 44f),
					Range(random, -0.25f, 0.25f),
					shade);
			}
		}

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
		for (var pass = 0; pass < 2; pass++)
		{
			// Pass 0 darkens the gaps a little down and right of the blade, a faint shadow. Pass 1 paints the blade.
			var offsetX = pass == 0 ? 4f : 0f;
			var offsetY = pass == 0 ? 9f : 0f;
			for (var y = (int)rootY - reach; y <= (int)rootY + reach; y++)
			{
				for (var x = (int)rootX - reach; x <= (int)rootX + reach; x++)
				{
					var (cover, tip) = Cover(x + 0.5f - rootX - offsetX, y + 0.5f - rootY - offsetY, heading, length, width, bend);
					if (cover <= 0f)
					{
						continue;
					}

					// The picture wraps at its edges, so it tiles.
					var index = (((y % Size) + Size) % Size) * Size + ((x % Size) + Size) % Size;
					if (pass == 0)
					{
						_values[index] *= 1f - 0.07f * cover;
					}
					else
					{
						var color = shade * (0.97f + 0.06f * Math.Clamp(tip, 0f, 1f));
						_values[index] = _values[index] * (1f - cover) + color * cover;
					}
				}
			}
		}
	}
}
