
class IPAddress:
    def __init__(self, _ip):
        self.ip = _ip
        self.mac = ""
        self.old_mac = ""
        self.free = 1
        self.hold = 0

    def setMac(self, _mac):
        self.mac = _mac

    def make_ip_unavailable(self):
        self.hold = 0
        self.free = 0

    def hold_address(self):
        self.hold = 1

    def release_address(self):
        self.hold = 0

    def make_ip_available(self):
        self.free = 1
        self.hold = 0
        self.old_mac = self.mac
