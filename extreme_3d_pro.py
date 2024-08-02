import hid
from typing import Literal, Tuple, Dict, Optional, List

# ids for the Extreme 3D Pro
_VID = 0x046D
_PID = 0xC215
_STICK_MAX = 1023
_STICK_FACTOR = 1.0 / _STICK_MAX * 2.0
_TWIST_MAX = 255
_TWIST_FACTOR = 1.0 / _TWIST_MAX * 2.0
_SLIDER_MAX = 255
_SLIDER_FACTOR = 1.0 / _SLIDER_MAX


class Extreme3DPro:
    def __init__(self,
                 vid=_VID,
                 pid=_PID,
                 serial=None,
                 path=None,
                 auto_update: bool = True) -> None:
        self.device = hid.Device(vid=vid, pid=pid, serial=serial, path=path)

        # read first report with blocking
        self.device.nonblocking = False
        self.event = self.device.read(7)
        self.device.nonblocking = True

        # record field
        self.auto_update = auto_update

    def _parse(self) -> None:
        # data structure (bits):
        # x[0:10], y[10:20], hat[20:24], twist[24:32], buttons_a[32:40], slider[40:48], buttons_b[48:56]
        # obtain from [Logitech3DPro](https://github.com/BenBrewerBowman/Arduino_Logitech_3D_Joystick/blob/master/Logitech3DPro/le3dp_rptparser2.0.h)

        # get first 4 bytes as uint32 and parse
        unaligned_bytes = self.event[0:4]
        uint_value = int.from_bytes(unaligned_bytes, byteorder='little')
        self._x = uint_value & 0x0000_03FF
        self._y = (uint_value & (0x3FF << 10)) >> 10
        self._hat = (uint_value & (0x0F << 20)) >> 20
        self._twist = (uint_value & (0xFF << 24)) >> 24

        # parse byte-aligned data
        buttons_a = self.event[4]
        buttons_b = self.event[6]
        self._buttons = buttons_a | (buttons_b << 8)
        self._slider = self.event[5]

    hat_pos_map: Dict[int, Tuple[int, int]] = {
        0: (0, 1),
        1: (1, 1),
        2: (1, 0),
        3: (1, -1),
        4: (0, -1),
        5: (-1, -1),
        6: (-1, 0),
        7: (-1, 1),
        8: (0, 0)
    }

    def update(self) -> bool:
        event = self.device.read(7)
        if event:
            self.event = event
            self._parse()
            return True
        return False

    @property
    def stick(self):
        if self.auto_update:
            self.update()

        return (self._x * _STICK_FACTOR - 1, self._y * _STICK_FACTOR - 1)

    @property
    def x(self):
        if self.auto_update:
            self.update()

        return self._x * _STICK_FACTOR - 1

    @property
    def y(self):
        if self.auto_update:
            self.update()

        return self._y * _STICK_FACTOR - 1

    @property
    def hat(self):
        if self.auto_update:
            self.update()

        return Extreme3DPro.hat_pos_map[self._hat]

    @property
    def buttons(self) -> List[int]:
        if self.auto_update:
            self.update()

        l: List[int] = []
        position: int = 0
        buttons = self._buttons
        while buttons:
            if buttons & 1:
                l.append(position + 1)
            buttons >>= 1
            position += 1
        return l

    @property
    def twist(self):
        if self.auto_update:
            self.update()

        return self._twist * _TWIST_FACTOR - 1

    @property
    def slider(self):
        if self.auto_update:
            self.update()

        return self._slider * _SLIDER_FACTOR

    def report_summary(self) -> str:
        return f"stick: ({self.x:.4f}, {self.y:.4f}), hat: {self.hat}, buttons: {self.buttons}, twist: {self.twist:.4f}, slider: {self.slider:.4f}"


device = Extreme3DPro(auto_update=False)
while True:
    if device.update():
        print(device.report_summary())
    else:
        pass
