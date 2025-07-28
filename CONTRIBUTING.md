# Contributing to Glorb

Thanks for your interest in contributing to Glorb! 🎉

## Development Setup

### Windows
```bash
git clone https://github.com/yourusername/glorb.git
cd glorb
pip install -r requirements.txt
pip install -e .
```

### Testing
```bash
glorb identify  # Test monitor detection
glorb rotate 0 90  # Test rotation
glorb b 0 0.5  # Test brightness
```

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and small

## Adding Platform Support

### Linux Support (Planned)
- Use `xrandr` for X11 displays
- Use `wlr-randr` for Wayland
- Implement brightness control via `/sys/class/backlight/`

### Structure
```python
# Platform detection
if sys.platform == "win32":
    from .windows import WindowsMonitorManager as MonitorManager
elif sys.platform == "linux":
    from .linux import LinuxMonitorManager as MonitorManager
```

## Pull Request Process

1. Fork the repo
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Update documentation if needed
6. Submit a pull request

## Reporting Issues

Please include:
- Operating system and version
- Python version
- Full error message
- Steps to reproduce

## Feature Requests

We're especially interested in:
- Linux/Wayland support
- Configuration profiles
- Multi-monitor presets
- Performance improvements