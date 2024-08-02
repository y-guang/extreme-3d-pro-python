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
_SLIDER_FACTOR = 1.0 / _SLIDER_MAX * 2.0


class Extreme3DProDrive:
    """
    A low-level interface for communicating with the Extreme 3D Pro joystick using the HID interface.

    The `Extreme3DProDrive` class serves as a thin wrapper around the HID interface, providing direct access to 
    the raw parameters of the joystick. It decodes the raw data from the HID device.

    This class is intended for use in scenarios where low-level access to joystick data is needed. For more 
    abstract and user-friendly operations, consider using the `Extreme3DPro` class.

    @param vid: the vendor id of the joystick
    @param pid: the product id of the joystick
    @param serial: the serial number of the joystick
    @param path: the path of the joystick
    @param nonblocking: whether the joystick's update is blocking or not
    """

    def __init__(self, vid=_VID, pid=_PID, serial=None, path=None, nonblocking=True):
        self.device = hid.Device(vid=vid, pid=pid, serial=serial, path=path)

        # read first report with blocking mode regardless of the parameter
        self.device.nonblocking = False
        self.event = self.device.read(7)
        self._parse()

        # set nonblocking mode according to the parameter
        self.device.nonblocking = nonblocking

    def _parse(self):
        """
        parse the event data (self.event) to get the joystick's state
        """
        # data structure (bits):
        # x[0:10], y[10:20], hat[20:24], twist[24:32], buttons_a[32:40], slider[40:48], buttons_b[48:56]
        # obtain from [Logitech3DPro](https://github.com/BenBrewerBowman/Arduino_Logitech_3D_Joystick/blob/master/Logitech3DPro/le3dp_rptparser2.0.h)

        # get first 4 bytes as uint32 and parse
        unaligned_bytes = self.event[0:4]
        uint_value = int.from_bytes(unaligned_bytes, byteorder='little')
        self.x = uint_value & 0x3FF
        self.y = (uint_value & (0x3FF << 10)) >> 10
        self.hat = (uint_value & (0x0F << 20)) >> 20
        self.twist = (uint_value & (0xFF << 24)) >> 24

        # parse byte-aligned data
        buttons_a = self.event[4]
        buttons_b = self.event[6]
        self.buttons = buttons_a | (buttons_b << 8)
        self.slider = self.event[5]

    def report_summary(self):
        """
        get a summary of the joystick's state

        @return: a string containing the joystick's state
        """
        return f"stick: ({self.x}, {self.y}), hat: {self.hat}, buttons: {self.buttons}, twist: {self.twist}, slider: {self.slider}"

    def update(self):
        """
        attempt to retrieve the newest event data from the joystick. if available, update all fields, otherwise keep old values.

        @return: whether the update was successful or not
        """
        event = self.device.read(7)
        if event:
            self.event = event
            self._parse()
            return True
        return False


class Extreme3DPro:
    """
    A high-level interface for interacting with the Extreme 3D Pro joystick, providing normalized input values.

    The `Extreme3DPro` class builds upon `Extreme3DProDrive`, offering more convenient and user-friendly properties
    for working with the joystick.

    @param vid: the vendor id of the joystick
    @param pid: the product id of the joystick
    @param serial: the serial number of the joystick
    @param path: the path of the joystick
    @param auto_update: whether the joystick's state should be updated automatically when accessing properties. 
           note, when set to True, calling two properties may get asynchronous two properties (one from the old state and one from the new state).

    @note: there is NO event buffer in the `Extreme3DPro` class. It only reflect what state the joystick is in at the moment of calling the property.
    """

    def __init__(self, vid=_VID, pid=_PID, serial=None, path=None,
                 auto_update: bool = True) -> None:
        self.device = Extreme3DProDrive(
            vid=vid, pid=pid, serial=serial, path=path)

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
        """
        update the joystick's state.

        @return: whether the update was successful or not
        """
        return self.device.update()

    @property
    def x(self):
        """
        get the joystick's x position

        @return: the joystick's x position. normalized to [-1, 1]
        """
        return self.device.x * _STICK_FACTOR - 1

    @property
    def y(self):
        """
        get the joystick's y position

        @return: the joystick's y position. normalized to [-1, 1]
        """
        return self.device.y * _STICK_FACTOR - 1

    @property
    def hat(self):
        """
        get the joystick's hat position

        @return: a tuple containing the x and y position of the hat. each value is either -1, 0, or 1.
                e.g. southwest: (-1, -1), north: (0, 1).
        """
        return Extreme3DPro.hat_pos_map[self.device.hat]

    @property
    def buttons(self) -> List[int]:
        """
        get the joystick's buttons

        @return: a list containing the numbers of the triggered buttons.
        """
        l: List[int] = []
        position: int = 0
        buttons = self.device.buttons
        while buttons:
            if buttons & 1:
                l.append(position + 1)
            buttons >>= 1
            position += 1
        return l

    @property
    def stick(self):
        """
        get the joystick's stick, i.e. x and y position in a tuple

        @return: a tuple containing the joystick's x and y position. each value is normalized to [-1, 1]
        """
        return (self.device.x * _STICK_FACTOR - 1, self.device.y * _STICK_FACTOR - 1)

    @property
    def twist(self):
        """
        get the joystick's twist position

        @return: the joystick's twist position. normalized to [-1, 1]
        """
        return self.device.twist * _TWIST_FACTOR - 1

    @property
    def slider(self):
        """
        get the joystick's slider position

        @return: the joystick's slider position. normalized to [-1, 1]
        """
        return self.device.slider * _SLIDER_FACTOR - 1

    def report_summary(self) -> str:
        return f"stick: ({self.x:.4f}, {self.y:.4f}), hat: {self.hat}, buttons: {self.buttons}, twist: {self.twist:.4f}, slider: {self.slider:.4f}"
