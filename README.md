# Extreme 3d Pro Python

A simple python library for interfacing with the Logitech Extreme 3D Pro joystick via HID on Windows System.

## How to Setup (Windows)

Add dependencies to your python environment:

```bash
pip install hid
pip install hidapi
```

Download the [hidapi](https://github.com/libusb/hidapi/releases). Unzip the file and copy the `hidapi.dll` to system32 folder. e.g. `C:\Windows\System32`.