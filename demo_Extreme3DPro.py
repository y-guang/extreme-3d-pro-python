from extreme_3d_pro import Extreme3DPro

device = Extreme3DPro()
while True:
    if device.update():
        print(device.report_summary())
    else:
        pass