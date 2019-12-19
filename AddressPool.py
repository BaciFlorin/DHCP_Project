from IPAddress import *

#de modificat pentru o cautare mai eficienta
class AddressPool():
    def __init__(self, _ipAddress, _mask):
        self.ips = []
        ip = []
        self.invertedMask = []
        self.nrIps = 0
        self.broadcastAddress = ""

        for x in _ipAddress.split('.'):
            ip.append(int(x))

        for x in _mask.split('.'):
            self.invertedMask.append(255-int(x))

        #calculul numarului de ips din spatiu
        for i in range(0, 4):
            if self.invertedMask[i] != 0:
                self.nrIps += self.invertedMask[i]*pow(2,8*(3-i))

        #aici se contruieste vectorul in care am toate adresele ip disponibile
        for i in range (1,self.nrIps):
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
        # atribuim penultima adresa din spatiu serverului si o scoatem din spatiul de adrese alocabil
        self.server_identifier = str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3])
        for client_ip in self.ips:
            if client_ip.ip == self.server_identifier:
                client = client_ip
        self.ips.remove(client)
        # determinam si adresa de broadcast din retea
        self.broadcastAddress = str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3] + 1)

    def getFreeAddress(self,_mac):
        ip = 0
        for x in self.ips:
            if x.free == 1 and x.hold != 1:
                x.holdAddress()
                x.setMac(_mac)
                ip = x
                break
        return ip

    def setAddressLock(self,_mac):
        #functie apelata in caz de clientul doreste acea adresa
        for x in self.ips:
            if x.mac == _mac:
                x.setAddress()
                break

    def unsetAddressLock(self,_mac):
        #functie apelata in caz de lease time expira sau clientul trimite mesajul DHCPRELEASE
        for x in self.ips:
            if x.mac == _mac:
                x.unsetAddress()
                break

    def setAddressUnreserved(self,_mac):
        #functie apelata in caz de adresa ip atribuita initial nu este validata de client
        #si astfel o facem disponibila pentru alte atribuiri
        for x in self.ips:
            if x.mac == _mac:
                x.releaseAddress()
                x.setMac("")
                break

    def findAddressMAC(self,_mac):
        ip=0
        for x in self.ips:
            if x.mac == _mac:
                ip = x
        return ip

    def findAddressIP(self,_ip):
        ip=0
        for x in self.ips:
            if x.ip == _ip:
                ip = x.ip
                break
        if ip==0:
            #log in care sa precizezi ca nu exista adresa in spatiul ala
            pass
        return ip

    def findOldAdress(self, _oldMac):
        ip = 0
        for x in self.ips:
            if x.oldmac == _oldMac:
                ip = x
                break
        return ip
