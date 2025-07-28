"""Monitor utilities for display detection, brightness control, and rotation"""

import win32api
import win32con
import win32gui
from ctypes import windll, wintypes, byref, Structure, c_int, c_uint, c_void_p, POINTER, WINFUNCTYPE
from ctypes.wintypes import DWORD, BOOL, HANDLE, HDC, RECT
try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

# Constants
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

# Monitor enumeration callback
MONITORENUMPROC = WINFUNCTYPE(BOOL, HANDLE, HDC, POINTER(RECT), c_void_p)

class PHYSICAL_MONITOR(Structure):
    _fields_ = [('hPhysicalMonitor', HANDLE), ('szPhysicalMonitorDescription', wintypes.WCHAR * 128)]

class MonitorUtils:
    def __init__(self):
        self.displays = []
        self.physical_monitors = {}
        self._detect_displays()
    
    def _detect_displays(self):
        """Detect all connected displays with detailed information"""
        self.displays = []
        
        # Get display devices
        device_index = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, device_index)
                if not device.DeviceName:
                    break
                
                # Only include active displays
                if not (device.StateFlags & DISPLAY_DEVICE_ACTIVE):
                    device_index += 1
                    continue
                
                # Get display settings
                try:
                    settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                    
                    # Clean up description
                    description = device.DeviceString
                    if "Generic PnP Monitor" in description:
                        description = f"Display {device_index + 1}"
                    
                    display_info = {
                        'id': device_index,
                        'name': device.DeviceName,
                        'description': description,
                        'width': settings.PelsWidth,
                        'height': settings.PelsHeight,
                        'frequency': settings.DisplayFrequency,
                        'orientation': settings.DisplayOrientation,
                        'primary': device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE != 0,
                        'active': True
                    }
                    self.displays.append(display_info)
                    print(f"Detected Monitor {device_index}: {description} ({settings.PelsWidth}x{settings.PelsHeight})")
                except Exception as e:
                    print(f"Error getting settings for device {device_index}: {e}")
                
                device_index += 1
            except Exception as e:
                print(f"Error enumerating device {device_index}: {e}")
                break
        
        # Ensure we have at least one display
        if not self.displays:
            self.displays = [{
                'id': 0,
                'name': 'Primary',
                'description': 'Primary Display',
                'width': 1920,
                'height': 1080,
                'frequency': 60,
                'orientation': 0,
                'primary': True,
                'active': True
            }]
        
        print(f"Total displays detected: {len(self.displays)}")
        
        # Get physical monitor handles for brightness control
        self._get_physical_monitors()
    
    def _get_physical_monitors(self):
        """Get physical monitor handles for brightness control"""
        try:
            def enum_callback(hmonitor, hdc, rect, data):
                try:
                    monitor_count = DWORD()
                    result = windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hmonitor, byref(monitor_count))
                    
                    if result and monitor_count.value > 0:
                        physical_monitors = (PHYSICAL_MONITOR * monitor_count.value)()
                        result = windll.dxva2.GetPhysicalMonitorsFromHMONITOR(hmonitor, monitor_count.value, physical_monitors)
                        
                        if result:
                            # Get monitor info using ctypes
                            from ctypes import sizeof, create_string_buffer
                            
                            class MONITORINFO(Structure):
                                _fields_ = [
                                    ('cbSize', DWORD),
                                    ('rcMonitor', RECT),
                                    ('rcWork', RECT),
                                    ('dwFlags', DWORD)
                                ]
                            
                            class MONITORINFOEX(Structure):
                                _fields_ = [
                                    ('cbSize', DWORD),
                                    ('rcMonitor', RECT),
                                    ('rcWork', RECT),
                                    ('dwFlags', DWORD),
                                    ('szDevice', wintypes.WCHAR * 32)
                                ]
                            
                            monitor_info = MONITORINFOEX()
                            monitor_info.cbSize = sizeof(MONITORINFOEX)
                            
                            if windll.user32.GetMonitorInfoW(hmonitor, byref(monitor_info)):
                                device_name = monitor_info.szDevice
                            else:
                                device_name = None
                            
                            if device_name:
                                for display in self.displays:
                                    if display['name'] == device_name:
                                        self.physical_monitors[display['id']] = physical_monitors[0].hPhysicalMonitor
                                        print(f"Physical monitor handle obtained for Monitor {display['id']}")
                                        break
                except Exception as e:
                    print(f"Error in enum callback: {e}")
                
                return True
            
            # Use ctypes to call EnumDisplayMonitors
            user32 = windll.user32
            user32.EnumDisplayMonitors.argtypes = [HDC, POINTER(RECT), MONITORENUMPROC, c_void_p]
            user32.EnumDisplayMonitors.restype = BOOL
            
            callback_func = MONITORENUMPROC(enum_callback)
            user32.EnumDisplayMonitors(None, None, callback_func, None)
            print(f"Physical monitors found: {len(self.physical_monitors)}")
        except Exception as e:
            print(f"Error getting physical monitors: {e}")
    
    def get_display_info(self, display_id=None):
        """Get information about displays"""
        if display_id is None:
            return self.displays
        
        for display in self.displays:
            if display['id'] == display_id:
                return display
        return None
    
    def get_brightness(self, display_id):
        """Get brightness level for a specific display (0-100)"""
        if display_id not in self.physical_monitors:
            print(f"No physical monitor handle for display {display_id}")
            return None
        
        try:
            min_brightness = DWORD()
            current_brightness = DWORD()
            max_brightness = DWORD()
            
            result = windll.dxva2.GetMonitorBrightness(
                self.physical_monitors[display_id],
                byref(min_brightness),
                byref(current_brightness),
                byref(max_brightness)
            )
            
            if result:
                # Convert to percentage
                brightness_range = max_brightness.value - min_brightness.value
                if brightness_range > 0:
                    percentage = ((current_brightness.value - min_brightness.value) / brightness_range) * 100
                    return int(percentage)
                else:
                    return int((current_brightness.value / max_brightness.value) * 100)
            
            print(f"Failed to get brightness for display {display_id}")
            return None
        except Exception as e:
            print(f"Error getting brightness for display {display_id}: {e}")
            return None
    
    def set_brightness(self, display_id, brightness):
        """Set brightness level for a specific display (0-100)"""
        if display_id not in self.physical_monitors:
            print(f"No physical monitor handle for display {display_id}")
            return False
        
        try:
            brightness = max(0, min(100, brightness))  # Clamp to 0-100
            
            min_brightness = DWORD()
            current_brightness = DWORD()
            max_brightness = DWORD()
            
            # Get current brightness range
            result = windll.dxva2.GetMonitorBrightness(
                self.physical_monitors[display_id],
                byref(min_brightness),
                byref(current_brightness),
                byref(max_brightness)
            )
            
            if result:
                # Convert percentage to actual value
                brightness_range = max_brightness.value - min_brightness.value
                if brightness_range > 0:
                    new_brightness = min_brightness.value + int((brightness / 100.0) * brightness_range)
                else:
                    new_brightness = int((brightness / 100.0) * max_brightness.value)
                
                result = windll.dxva2.SetMonitorBrightness(
                    self.physical_monitors[display_id],
                    DWORD(new_brightness)
                )
                
                if result:
                    print(f"Brightness set to {brightness}% for display {display_id}")
                    return True
                else:
                    print(f"Failed to set brightness for display {display_id}")
            
            return False
        except Exception as e:
            print(f"Error setting brightness for display {display_id}: {e}")
            return False
    
    def rotate_display(self, display_id, angle):
        """Rotate display to specific angle (0, 90, 180, 270)"""
        display = self.get_display_info(display_id)
        if not display:
            return False
        
        try:
            # Map angles to Windows rotation constants
            rotation_map = {0: 0, 90: 1, 180: 2, 270: 3}
            if angle not in rotation_map:
                return False
            
            # Get current display settings
            settings = win32api.EnumDisplaySettings(display['name'], win32con.ENUM_CURRENT_SETTINGS)
            
            # Set new orientation
            settings.DisplayOrientation = rotation_map[angle]
            
            # For 90/270 degree rotations, swap width and height
            if angle in [90, 270]:
                settings.PelsWidth, settings.PelsHeight = settings.PelsHeight, settings.PelsWidth
            
            # Apply the change using win32api
            result = win32api.ChangeDisplaySettingsEx(
                display['name'], 
                settings, 
                0x00000001  # CDS_UPDATEREGISTRY
            )
            
            if result == 0:  # DISP_CHANGE_SUCCESSFUL
                # Update our display info
                self._detect_displays()
                return True
            
            return False
        except Exception as e:
            print(f"Error rotating display: {e}")
            return False
    
    def get_display_modes(self, display_id):
        """Get available display modes for a display"""
        display = self.get_display_info(display_id)
        if not display:
            return []
        
        modes = []
        mode_index = 0
        
        while True:
            try:
                settings = win32api.EnumDisplaySettings(display['name'], mode_index)
                if settings:
                    mode = {
                        'width': settings.PelsWidth,
                        'height': settings.PelsHeight,
                        'frequency': settings.DisplayFrequency,
                        'bits_per_pixel': settings.BitsPerPel
                    }
                    if mode not in modes:
                        modes.append(mode)
                    mode_index += 1
                else:
                    break
            except:
                break
        
        return modes
    
    def set_display_mode(self, display_id, width, height, frequency=None):
        """Set display resolution and refresh rate"""
        display = self.get_display_info(display_id)
        if not display:
            return False
        
        try:
            settings = win32api.EnumDisplaySettings(display['name'], win32con.ENUM_CURRENT_SETTINGS)
            settings.PelsWidth = width
            settings.PelsHeight = height
            
            if frequency:
                settings.DisplayFrequency = frequency
            
            result = win32api.ChangeDisplaySettingsEx(
                display['name'],
                settings,
                0x00000001  # CDS_UPDATEREGISTRY
            )
            
            if result == 0:  # DISP_CHANGE_SUCCESSFUL
                self._detect_displays()
                return True
            
            return False
        except Exception as e:
            print(f"Error setting display mode: {e}")
            return False
    
    def __del__(self):
        """Cleanup physical monitor handles"""
        try:
            for handle in self.physical_monitors.values():
                windll.dxva2.DestroyPhysicalMonitor(handle)
        except:
            pass