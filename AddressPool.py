from IPAddress import *

class AddressPool():
    def __init__(self,_ipAddress,_mask):
        self.ips=[]
        ip=[]
        imask=[]
        nrIps=0
        for x in _ipAddress.split('.'):
            ip.append(int(x))
        for x in _mask.split('.'):
            imask.append(255-int(x))
        for i in range(0,4):
            if imask[i]!=0:
                nrIps+=imask[i]*pow(2,8*(3-i))

        #aici se contruieste vectorul in care am toate adresele ip disponobile
        for i in range (1,nrIps):
            ip[3]+=1
            if ip[3]>255:
                ip[3]=0
                ip[2]+=1
                if ip[2]>255:
                    ip[2]=0
                    ip[1]+=1
                    if ip[1]>255:
                        ip[1]=0
                        ip[0]+=1
            self.ips.append(IPAddress(str(ip[0])+"."+str(ip[1])+"."+str(ip[2])+"."+str(ip[3])))

    def getFreeAddress(self,_mac):
        ip=""
        for x in self.ips:
            if x.free==1 and x.hold!=1:
                x.reserve()
                x.setMac(_mac)
                ip=x.ip
                break
        return ip

    def setAddressLocked(self,_mac):
        for x in self.ips:
            if x.mac==_mac:
                x.ocupy()
                break

    def setAddressUnreserve(self,_mac):
        for x in self.ips:
            if x.mac==_mac:
                x.unreserve()
                break






