import rotatescreen
import keyboard
from pystray import Icon, Menu, MenuItem
from PIL import Image
import threading

screen = rotatescreen.get_primary_display()


rotations = [0, 90, 180, 270]
current_rotation_index = 0


def cycle_rotation():
    global current_rotation_index
    screen.rotate_to(rotations[current_rotation_index])
    current_rotation_index = (current_rotation_index + 1) % len(rotations)


def setup_hotkey():
    keyboard.add_hotkey("ctrl+alt+f12", cycle_rotation)
    keyboard.wait()


def load_icon(icon_path):
    image = Image.open(icon_path)
    return image


def on_exit(icon, item):
    icon.stop()
    print("Exiting the application.")
    exit(0)


def main():
    menu = Menu(MenuItem("Rotate Screen", cycle_rotation), MenuItem("Exit", on_exit))

    tray_icon = Icon("Screen Rotator", load_icon("monicon.ico"), "Screen Rotator", menu)

    hotkey_thread = threading.Thread(target=setup_hotkey, daemon=True)
    hotkey_thread.start()

    tray_icon.run()


if __name__ == "__main__":
    main()
