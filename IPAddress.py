
class IPAddress():
    def __init__(self,_ip):
        self.ip = _ip
        self.mac = ""
        self.oldmac = ""
        self.free = 1
        self.hold = 0

    def setMac(self, _mac):
        self.mac = _mac

    def setAddress(self):
        self.hold = 0
        self.free = 0

    def holdAddress(self):
        self.hold = 1

    def unsetAddress(self):
        self.free = 1
        self.hold = 0
        #tinem minte ultima statie care a avut adresa
        self.oldmac = self.mac

    def releaseAddress(self):
        self.hold = 0

    def setLeaseTime(self, _leaseTime):
        self.leaseTime = _leaseTime



