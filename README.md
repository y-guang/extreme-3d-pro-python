# Extreme 3d Pro Python

A simple python library for interfacing with the Logitech Extreme 3D Pro joystick via HID on Windows System.

## How to Setup (Windows)

First, install the official software from [Logitech's website](https://support.logi.com/hc/en-us/articles/360024843033--Downloads-Extreme-3D-Pro).

Add dependencies to your python environment:

```bash
pip install hid
pip install hidapi
```

Download the [hidapi](https://github.com/libusb/hidapi/releases). Unzip the file and copy the `hidapi.dll` to system32 folder. e.g. `C:\Windows\System32`.

## How to use

copy the `Extreme3dPro.py` to your project folder.

Then, import `Extreme3DPro` class. see example in `demo_Extreme3dPro.py`.

Note, the `Extreme3DPro` class is generally recommended. use `Extreme3DProDrive` only when you have a specific use case.

## Acknowledgement

The hid decode approach is obtained from the [BenBrewerBowman/Logitech3DPro](https://github.com/BenBrewerBowman/Arduino_Logitech_3D_Joystick/blob/master/Logitech3DPro/le3dp_rptparser2.0.h)

