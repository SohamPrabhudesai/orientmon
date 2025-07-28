#!/usr/bin/env python3
"""Glorb - CLI Monitor Management Tool"""

import sys
import argparse
import win32api
import win32con
from ctypes import windll, wintypes, byref, Structure
from ctypes.wintypes import DWORD, HANDLE
try:
    import wmi
except ImportError:
    pass

class PHYSICAL_MONITOR(Structure):
    _fields_ = [('hPhysicalMonitor', HANDLE), ('szPhysicalMonitorDescription', wintypes.WCHAR * 128)]

class MonitorManager:
    def __init__(self):
        self.displays = self._detect_displays()
        self.physical_monitors = self._get_physical_monitors()
    
    def _detect_displays(self):
        displays = []
        device_index = 0
        
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, device_index)
                if not device.DeviceName:
                    break
                
                if device.StateFlags & 0x00000001:  # DISPLAY_DEVICE_ACTIVE
                    settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                    displays.append({
                        'id': device_index,
                        'name': device.DeviceName,
                        'description': device.DeviceString,
                        'width': settings.PelsWidth,
                        'height': settings.PelsHeight,
                        'primary': device.StateFlags & 0x00000004 != 0  # DISPLAY_DEVICE_PRIMARY_DEVICE
                    })
                device_index += 1
            except:
                break
        
        return displays
    
    def _get_physical_monitors(self):
        """Get physical monitor handles for brightness control"""
        physical_monitors = {}
        try:
            import win32gui
            from ctypes import POINTER, c_void_p, WINFUNCTYPE
            from ctypes.wintypes import RECT, HDC, BOOL
            
            MONITORENUMPROC = WINFUNCTYPE(BOOL, HANDLE, HDC, POINTER(RECT), c_void_p)
            
            def enum_callback(hmonitor, hdc, rect, data):
                try:
                    monitor_count = DWORD()
                    if windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hmonitor, byref(monitor_count)):
                        if monitor_count.value > 0:
                            physical_monitors_array = (PHYSICAL_MONITOR * monitor_count.value)()
                            if windll.dxva2.GetPhysicalMonitorsFromHMONITOR(hmonitor, monitor_count.value, physical_monitors_array):
                                # Map to display ID (simplified)
                                for i, display in enumerate(self.displays):
                                    if i < monitor_count.value:
                                        physical_monitors[display['id']] = physical_monitors_array[i].hPhysicalMonitor
                except:
                    pass
                return True
            
            callback_func = MONITORENUMPROC(enum_callback)
            windll.user32.EnumDisplayMonitors(None, None, callback_func, None)
        except:
            pass
        
        return physical_monitors
    
    def identify(self):
        """List all detected monitors"""
        print("Detected monitors:")
        for display in self.displays:
            primary = " (Primary)" if display['primary'] else ""
            print(f"  {display['id']}: {display['description']} - {display['width']}x{display['height']}{primary}")
    
    def rotate(self, monitor_id, angle):
        """Rotate monitor to specific angle"""
        if monitor_id >= len(self.displays):
            print(f"Error: Monitor {monitor_id} not found")
            return False
        
        display = self.displays[monitor_id]
        rotation_map = {0: 0, 90: 1, 180: 2, 270: 3}
        
        if angle not in rotation_map:
            print(f"Error: Invalid angle {angle}. Use 0, 90, 180, or 270")
            return False
        
        try:
            # Get fresh settings each time
            settings = win32api.EnumDisplaySettings(display['name'], win32con.ENUM_CURRENT_SETTINGS)
            current_orientation = settings.DisplayOrientation
            
            # Set new orientation
            settings.DisplayOrientation = rotation_map[angle]
            
            # Handle width/height swapping based on orientation change
            if (current_orientation in [0, 2] and angle in [90, 270]) or \
               (current_orientation in [1, 3] and angle in [0, 180]):
                settings.PelsWidth, settings.PelsHeight = settings.PelsHeight, settings.PelsWidth
            
            result = win32api.ChangeDisplaySettingsEx(display['name'], settings, 0x00000001)
            
            if result == 0:
                print(f"Monitor {monitor_id} rotated to {angle}°")
                # Refresh display info and physical monitors
                self.displays = self._detect_displays()
                self.physical_monitors = self._get_physical_monitors()
                return True
            else:
                print(f"Failed to rotate monitor {monitor_id} (error code: {result})")
                return False
        except Exception as e:
            print(f"Error rotating monitor: {e}")
            return False
    
    def brightness(self, monitor_id, level):
        """Set monitor brightness (0.0 to 1.0)"""
        if monitor_id >= len(self.displays):
            print(f"Error: Monitor {monitor_id} not found")
            return False
        
        brightness_percent = max(0, min(100, int(level * 100)))
        
        # Try laptop brightness first (WMI method)
        if self._set_laptop_brightness(brightness_percent):
            print(f"Monitor {monitor_id} brightness set to {brightness_percent}%")
            return True
        
        # Try DDC/CI for external monitors
        self.physical_monitors = self._get_physical_monitors()
        
        if monitor_id not in self.physical_monitors:
            print(f"Error: Brightness control not supported for monitor {monitor_id}")
            return False
        
        try:
            handle = self.physical_monitors[monitor_id]
            
            # Get current range and calculate proper value
            min_brightness = DWORD()
            current_brightness = DWORD()
            max_brightness = DWORD()
            
            if windll.dxva2.GetMonitorBrightness(handle, byref(min_brightness), byref(current_brightness), byref(max_brightness)):
                brightness_range = max_brightness.value - min_brightness.value
                if brightness_range > 0:
                    new_brightness = min_brightness.value + int((brightness_percent / 100.0) * brightness_range)
                else:
                    new_brightness = int((brightness_percent / 100.0) * max_brightness.value)
                
                if windll.dxva2.SetMonitorBrightness(handle, DWORD(new_brightness)):
                    print(f"Monitor {monitor_id} brightness set to {brightness_percent}%")
                    return True
            
            print(f"Failed to set brightness for monitor {monitor_id}")
            return False
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False
    
    def _set_laptop_brightness(self, brightness_percent):
        """Set laptop brightness using WMI"""
        try:
            import wmi
            c = wmi.WMI(namespace='wmi')
            
            # Get brightness methods
            brightness_methods = c.WmiMonitorBrightnessMethods()[0]
            
            # Set brightness
            brightness_methods.WmiSetBrightness(brightness_percent, 0)
            return True
        except:
            # Fallback: try powershell method
            try:
                import subprocess
                cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{brightness_percent})"'
                result = subprocess.run(cmd, shell=True, capture_output=True)
                return result.returncode == 0
            except:
                return False

def main():
    parser = argparse.ArgumentParser(description='Glorb - Monitor Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # identify command
    subparsers.add_parser('identify', help='List all detected monitors')
    
    # rotate command
    rotate_parser = subparsers.add_parser('rotate', help='Rotate monitor')
    rotate_parser.add_argument('monitor', type=int, help='Monitor ID')
    rotate_parser.add_argument('angle', type=int, choices=[0, 90, 180, 270], help='Rotation angle')
    
    # brightness command
    brightness_parser = subparsers.add_parser('b', help='Set monitor brightness')
    brightness_parser.add_argument('monitor', type=int, help='Monitor ID')
    brightness_parser.add_argument('level', type=float, help='Brightness level (0.0 to 1.0)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MonitorManager()
    
    if args.command == 'identify':
        manager.identify()
    elif args.command == 'rotate':
        manager.rotate(args.monitor, args.angle)
    elif args.command == 'b':
        manager.brightness(args.monitor, args.level)

if __name__ == '__main__':
    main()