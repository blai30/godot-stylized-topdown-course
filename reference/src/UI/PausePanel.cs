using Godot;
using TopDownTemplate.World;

namespace TopDownTemplate.UI;

// A pause panel: Escape pauses the game and opens it, and its controls change the hour, VSync, and the sun's shadows.
public partial class PausePanel : Control
{
	// The clock whose time of day the slider sets, and the sun whose shadows the toggle switches.
	[Export] public DayClock? Clock { get; set; }
	[Export] public DirectionalLight3D? Sun { get; set; }

	private HSlider _timeSlider = null!;
	private CheckButton _vsyncToggle = null!;
	private CheckButton _shadowsToggle = null!;

	public override void _Ready()
	{
		// The panel keeps running while the tree is paused, and so do its children.
		ProcessMode = ProcessModeEnum.Always;
		Visible = false;

		_timeSlider = GetNode<HSlider>("%TimeSlider");
		_vsyncToggle = GetNode<CheckButton>("%VsyncToggle");
		_shadowsToggle = GetNode<CheckButton>("%ShadowsToggle");

		_timeSlider.ValueChanged += value =>
		{
			if (Clock is not null)
			{
				Clock.TimeOfDay = (float)value;
			}
		};
		_vsyncToggle.Toggled += enabled => DisplayServer.WindowSetVsyncMode(enabled ? DisplayServer.VSyncMode.Enabled : DisplayServer.VSyncMode.Disabled);
		_shadowsToggle.Toggled += enabled =>
		{
			if (Sun is not null)
			{
				Sun.ShadowEnabled = enabled;
			}
		};
		GetNode<Button>("%ResumeButton").Pressed += () => SetOpen(false);
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (!@event.IsActionPressed("ui_cancel"))
		{
			return;
		}

		SetOpen(!Visible);
		GetViewport().SetInputAsHandled();
	}

	private void SetOpen(bool open)
	{
		if (open)
		{
			ShowCurrentSettings();
		}

		Visible = open;
		GetTree().Paused = open;
	}

	// The controls show what the game has now, without changing it.
	private void ShowCurrentSettings()
	{
		if (Clock is not null)
		{
			_timeSlider.SetValueNoSignal(Clock.TimeOfDay);
		}

		_vsyncToggle.SetPressedNoSignal(DisplayServer.WindowGetVsyncMode() != DisplayServer.VSyncMode.Disabled);
		if (Sun is not null)
		{
			_shadowsToggle.SetPressedNoSignal(Sun.ShadowEnabled);
		}
	}
}
