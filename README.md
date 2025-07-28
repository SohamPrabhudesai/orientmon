# Glorb 🖥️

A fun and powerful CLI tool for monitor management across platforms.

## Features

- **Monitor Detection** - Auto-detect and identify all connected displays
- **Screen Rotation** - Rotate displays to any orientation (0°, 90°, 180°, 270°)
- **Brightness Control** - Adjust brightness for both laptop and external monitors
- **Cross-Platform** - Windows support now, Linux coming soon!
- **Simple CLI** - Easy-to-remember commands

## Installation

### Windows

```bash
git clone https://github.com/yourusername/glorb.git
cd glorb
pip install -e .
```

### Requirements
- Python 3.7+
- Windows 10/11

## Usage

### List all monitors
```bash
glorb identify
```

### Rotate a monitor
```bash
glorb rotate 0 90    # Rotate monitor 0 to 90 degrees
glorb rotate 1 180   # Rotate monitor 1 to 180 degrees
```

### Control brightness
```bash
glorb b 0 0.75       # Set monitor 0 brightness to 75%
glorb b 1 0.5        # Set monitor 1 brightness to 50%
```

## Examples

```bash
# Check what monitors you have
$ glorb identify
Detected monitors:
  0: Intel(R) Iris(R) Xe Graphics - 1920x1080 (Primary)
  1: Dell U2720Q - 3840x2160

# Rotate your laptop screen
$ glorb rotate 0 90
Monitor 0 rotated to 90°

# Dim your external monitor
$ glorb b 1 0.3
Monitor 1 brightness set to 30%
```

## Platform Support

| Platform | Status | Features |
|----------|--------|----------|
| Windows  | ✅ Ready | Full support |
| Linux    | 🚧 Coming Soon | Planned for v2.0 |
| macOS    | 📋 Planned | Future release |

## Development

### Windows Development
```bash
git clone https://github.com/yourusername/glorb.git
cd glorb
pip install -r requirements.txt
python glorb.py identify  # Test it out
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on your platform
5. Submit a pull request

## Roadmap

- [x] Windows monitor detection
- [x] Screen rotation
- [x] Brightness control (laptop + external)
- [ ] Linux support (X11/Wayland)
- [ ] Configuration profiles
- [ ] Multi-monitor presets
- [ ] Hotkey support
- [ ] GUI companion app

## Why "Glorb"?

Because it's fun to type `glorb rotate 0 90` and watch your screen flip! 🎯

## License

MIT License - see [LICENSE](LICENSE) for details.

## Troubleshooting

### Brightness not working
- **Laptop displays**: Should work with WMI on Windows
- **External monitors**: Requires DDC/CI support (most modern monitors)
- **Older monitors**: May not support brightness control

### Rotation issues
- Ensure graphics drivers are up to date
- Some rotations may not be supported by all graphics cards
- Try different angles if one doesn't work

## Credits

Built with ❤️ for the multi-monitor community.