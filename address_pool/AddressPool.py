from address_pool.IPAddress import *


class AddressPool:
    def __init__(self, _ipAddress, _mask):
        self.ips = []
        ip = []
        self.invertedMask = []
        self.nrIps = 0
        self.broadcastAddress = ""
        self.address_network = _ipAddress

        for x in _ipAddress.split('.'):
            ip.append(int(x))

        for x in _mask.split('.'):
            self.invertedMask.append(255-int(x))

        # find the number of ips in our address space
        for i in range(0, 4):
            if self.invertedMask[i] != 0:
                self.nrIps += self.invertedMask[i]*pow(2,8*(3-i))

        # Build the address pool
        for i in range(1, self.nrIps):
            ip[3] += 1
            if ip[3] > 255:
                ip[3] = 0
                ip[2] += 1
                if ip[2] > 255:
                    ip[2] = 0
                    ip[1] += 1
                    if ip[1] > 255:
                        ip[1] = 0
                        ip[0] += 1
            self.ips.append(IPAddress(str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3])))

        # Assign an ip address to server
        self.server_identifier = str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3])
        for client_ip in self.ips:
            if client_ip.ip == self.server_identifier:
                self.ips.remove(client_ip)

        # find broadcast address
        self.broadcastAddress = str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3] + 1)

    def get_free_address(self, _mac):
        ip = 0
        for x in self.ips:
            if x.free == 1 and x.hold != 1:
                x.hold_address()
                x.setMac(_mac)
                ip = x
                break
        return ip

    def make_unaivailable_an_ip(self, _mac):
        for x in self.ips:
            if x.mac == _mac:
                x.make_ip_unavailable()
                break

    def make_available_an_ip(self, _mac):
        for x in self.ips:
            if x.mac == _mac:
                x.make_ip_available()
                break

    def realease_an_ip(self, _mac):
        for x in self.ips:
            if x.mac == _mac:
                x.release_address()
                x.setMac("")
                break

    def find_ip_after_mac(self, _mac):
        for x in self.ips:
            if x.mac == _mac:
                return x
        return ""

    def find_address_IP(self, _ip):
        for x in self.ips:
            if x.ip == _ip:
                return x
        return ""

    def find_old_address(self, _old_mac):
        for x in self.ips:
            if x.old_mac == _old_mac:
                return x
        return ""
    
    def get_a_new_ip_for_client(self, mac, options):
        oldIp = self.find_old_address(mac)
        if oldIp != "":
            if oldIp.free != 0 and oldIp.hold != 1:
                # cazul in care se ia o adresa care a fost deja a clientului respectiv
                oldIp.setMac(mac)
                oldIp.hold_address()
                return oldIp.ip
            
        elif 50 in options:
            requested_ip = self.find_address_IP(options[50])
            if requested_ip != "":
                if requested_ip.free == 1 and requested_ip.hold == 0:
                    requested_ip.setMac(mac)
                    requested_ip.hold_address()
                    return requested_ip.ip
        new_ip = self.get_free_address(mac)
        new_ip.setMac(mac)
        new_ip.hold_address()
        return new_ip.ip
