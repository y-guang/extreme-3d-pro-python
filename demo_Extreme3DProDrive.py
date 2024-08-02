from extreme_3d_pro import Extreme3DProDrive

device = Extreme3DProDrive()
while True:
    if device.update():
        print(device.report_summary())
    else:
        pass