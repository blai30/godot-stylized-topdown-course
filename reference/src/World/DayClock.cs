using Godot;

namespace TopDownTemplate.World;

// Drives the day animation from a time of day, so a slider, a save file, or a cutscene can set the hour.
[Tool]
public partial class DayClock : AnimationPlayer
{
	private static readonly StringName DayAnimation = "day";
	private static readonly StringName RimColorGlobal = "rim_color";
	private static readonly StringName RimStrengthGlobal = "rim_strength";

	private float _timeOfDay = 0.5f;
	private int _hour = -1;
	private Color _rimColor = new("C6E4FF");
	private float _rimStrength = 0.3f;

	// The time of day from 0 (midnight) to 1, with noon at 0.5.
	[Export(PropertyHint.Range, "0,1,0.001")]
	public float TimeOfDay
	{
		get => _timeOfDay;
		set
		{
			_timeOfDay = Mathf.PosMod(value, 1f);
			Apply();
		}
	}

	// How many real seconds a whole day takes at Speed 1.
	[Export] public float DayLengthSeconds { get; set; } = 600f;

	// A multiplier on how fast the day passes.
	[Export] public float Speed { get; set; } = 1f;

	// Whether the day passes at all. Turn it off to hold one hour.
	[Export] public bool Running { get; set; } = true;

	// The color of the soft rim on surfaces. The day animation keys it, and it goes to the rim_color shader global.
	[Export]
	public Color RimColor
	{
		get => _rimColor;
		set
		{
			_rimColor = value;
			RenderingServer.GlobalShaderParameterSet(RimColorGlobal, value);
		}
	}

	// How strong the soft rim is, from 0 to 1. The day animation keys it, and it goes to the rim_strength shader global.
	[Export(PropertyHint.Range, "0,1,0.01")]
	public float RimStrength
	{
		get => _rimStrength;
		set
		{
			_rimStrength = value;
			RenderingServer.GlobalShaderParameterSet(RimStrengthGlobal, value);
		}
	}

	public override void _Ready()
	{
		Apply();
	}

	public override void _Process(double delta)
	{
		if (Engine.IsEditorHint() || !Running)
		{
			return;
		}

		TimeOfDay += (float)delta * Speed / DayLengthSeconds;
		PrintHour();
	}

	// Puts every animated property where the day animation has it at the current time of day.
	private void Apply()
	{
		if (!IsInsideTree() || !HasAnimation(DayAnimation))
		{
			return;
		}

		AssignedAnimation = DayAnimation;
		Seek(_timeOfDay * GetAnimation(DayAnimation).Length, true);
	}

	private void PrintHour()
	{
		var hour = (int)(_timeOfDay * 24f);
		if (hour == _hour)
		{
			return;
		}

		_hour = hour;
		GD.Print($"{hour:00}:00");
	}
}
