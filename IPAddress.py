
class IPAddress():
    def __init__(self,_ip):
        self.ip=_ip
        self.mac=0x000000000000
        self.oldmac=0x000000000000
        self.leaseTime=0
        self.free=1
        self.hold=0
        #aici e ok sa pui si optiunile si paramentrii de configurare, sa ii ai

    def setMac(self,_mac):
        self.mac=_mac

    def ocupy(self):
        self.free=0

    def reserve(self):
        self.hold=1

    def unocupy(self):
        self.free=1

    def unreserve(self):
        self.hold=0


